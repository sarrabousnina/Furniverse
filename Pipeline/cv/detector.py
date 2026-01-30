import torch
import numpy as np
from ultralytics import YOLO

class FurnitureDetector:
    """
    YOLO-based furniture detector.
    """

    def __init__(self):
        
        self.model_path = "models/best.pt" 

        print(f"[INFO] Loading YOLO model from: {self.model_path}")

        # Auto device selection
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"[INFO] Using device: {self.device.upper()}")

        with open(self.model_path, "rb") as f:
            print(f"[INFO] Model file size: {f.seek(0, 2)} bytes")

        # Load YOLO model
        try:
            self.model = YOLO(self.model_path)
            self.model.to(self.device)
            print("[INFO] YOLO model loaded successfully")
        except Exception as e:
            raise RuntimeError(
                f"Failed to load YOLO model at {self.model_path}\n{e}"
            )

    def detect(self, image, conf: float = 0.5):
        """
        Detect furniture objects in an image.

        Args:
            image (str | np.ndarray): Path or OpenCV image
            conf (float): Confidence threshold

        Returns:
            List of dicts:
            [
                {"class": "chair", "confidence": 0.92, "box": [x1, y1, x2, y2]},
                ...
            ]
        """
        if not isinstance(image, (str, np.ndarray)):
            raise TypeError("image must be path or numpy array")

        results = self.model(image, conf=conf, device=self.device, verbose=False)

        detections = []
        for result in results:
            if result.boxes is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            scores = result.boxes.conf.cpu().numpy()
            class_ids = result.boxes.cls.cpu().numpy().astype(int)

            for box, score, cls_id in zip(boxes, scores, class_ids):
                detections.append({
                    "class": result.names[cls_id],
                    "confidence": float(score),
                    "box": box.tolist()
                })

        return detections
