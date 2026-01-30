"""
Tripo3D API Integration - Generate 3D models from product images
"""
import os
import time
import requests
from typing import Dict, Optional
from pathlib import Path
import json

TRIPO_API_URL = "https://api.tripo3d.ai/v2/openapi"

class TripoGenerator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.cache_file = Path(__file__).parent / "3d_model_cache.json"
        self.models_dir = Path(__file__).parent.parent / "Frontend" / "public" / "models"
        self.models_dir.mkdir(parents=True, exist_ok=True)
        self.cache = self._load_cache()
    
    def _load_cache(self) -> Dict:
        """Load cache from file"""
        if self.cache_file.exists():
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_cache(self):
        """Save cache to file"""
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)
    
    def check_cache(self, image_url: str) -> Optional[str]:
        """Check if model already generated for this image"""
        cached = self.cache.get(image_url)
        if cached:
            model_path = self.models_dir / cached["filename"]
            if model_path.exists():
                print(f"✅ Cache hit for: {image_url}")
                return f"/models/{cached['filename']}"
        return None
    
    def upload_image(self, image_url: str) -> str:
        """Upload image to Tripo and get image token"""
        print(f"📤 Uploading image to Tripo: {image_url}")
        
        # Download image first
        img_response = requests.get(image_url)
        if img_response.status_code != 200:
            raise Exception(f"Failed to download image: {img_response.status_code}")
        
        # Upload to Tripo
        files = {'file': ('image.jpg', img_response.content, 'image/jpeg')}
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        response = requests.post(
            f"{TRIPO_API_URL}/upload",
            headers=headers,
            files=files
        )
        
        if response.status_code != 200:
            raise Exception(f"Tripo upload failed: {response.status_code} - {response.text}")
        
        data = response.json()
        if data.get('code') != 0:
            raise Exception(f"Tripo upload error: {data}")
        
        image_token = data['data']['image_token']
        print(f"✅ Image uploaded, token: {image_token}")
        return image_token
    
    def create_task(self, image_token: str) -> str:
        """Create 3D generation task"""
        print(f"🎯 Creating Tripo task...")
        
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            "type": "image_to_model",
            "model_version": "v2.5-20250123",
            "file": {
                "type": "jpg",
                "file_token": image_token
            }
        }
        
        response = requests.post(
            f"{TRIPO_API_URL}/task",
            headers=headers,
            json=payload
        )
        
        if response.status_code != 200:
            raise Exception(f"Task creation failed: {response.status_code} - {response.text}")
        
        data = response.json()
        if data.get('code') != 0:
            raise Exception(f"Tripo task error: {data}")
        
        task_id = data['data']['task_id']
        print(f"✅ Task created: {task_id}")
        return task_id
    
    def poll_task(self, task_id: str, max_attempts: int = 60) -> str:
        """Poll task until completion"""
        print(f"⏳ Polling task: {task_id}")
        
        headers = {'Authorization': f'Bearer {self.api_key}'}
        
        for attempt in range(max_attempts):
            response = requests.get(
                f"{TRIPO_API_URL}/task/{task_id}",
                headers=headers
            )
            
            if response.status_code != 200:
                raise Exception(f"Status check failed: {response.status_code}")
            
            data = response.json()
            status = data['data']['status']
            progress = data['data'].get('progress', 0)
            
            print(f"  Attempt {attempt + 1}/{max_attempts}: {status} ({progress}%)")
            
            if status == 'success':
                model_url = data['data'].get('output', {}).get('pbr_model')
                if not model_url:
                    model_url = data['data'].get('result', {}).get('pbr_model', {}).get('url')
                
                if model_url:
                    print(f"✅ Task completed! Model URL: {model_url}")
                    return model_url
                else:
                    raise Exception("Task succeeded but no model URL found")
            
            if status == 'failed':
                raise Exception("Tripo task failed")
            
            time.sleep(3)
        
        raise Exception("Task timed out")
    
    def download_model(self, model_url: str, product_id: str) -> str:
        """Download GLB model and save locally"""
        print(f"💾 Downloading model...")
        
        response = requests.get(model_url)
        if response.status_code != 200:
            raise Exception(f"Failed to download model: {response.status_code}")
        
        filename = f"product-{product_id}.glb"
        filepath = self.models_dir / filename
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Model saved: {filepath} ({len(response.content)} bytes)")
        return filename
    
    def generate_model(self, image_url: str, product_id: str, product_name: str) -> Dict:
        """Complete workflow: generate 3D model from image"""
        print(f"\n🚀 Generating 3D model for: {product_name}")
        print(f"   Product ID: {product_id}")
        print(f"   Image: {image_url}")
        
        # Check cache
        cached_url = self.check_cache(image_url)
        if cached_url:
            return {
                "success": True,
                "model_url": cached_url,
                "cached": True
            }
        
        try:
            # Step 1: Upload image
            image_token = self.upload_image(image_url)
            
            # Step 2: Create task
            task_id = self.create_task(image_token)
            
            # Step 3: Poll for completion
            tripo_model_url = self.poll_task(task_id)
            
            # Step 4: Download and save locally
            filename = self.download_model(tripo_model_url, product_id)
            
            # Step 5: Update cache
            self.cache[image_url] = {
                "filename": filename,
                "task_id": task_id,
                "product_id": product_id,
                "product_name": product_name
            }
            self._save_cache()
            
            return {
                "success": True,
                "model_url": f"/models/{filename}",
                "task_id": task_id,
                "cached": False
            }
        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
