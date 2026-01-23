# Furniverse Backend API

Minimal FastAPI backend for the Furniverse hackathon project.

## Setup

**Virtual environment is already created. To activate it:**

**Windows (Command Prompt):**
```bash
cd Backend
venv\Scripts\activate
```

**Windows (PowerShell):**
```bash
cd Backend
venv\Scripts\Activate.ps1
```

**Mac/Linux:**
```bash
cd Backend
source venv/bin/activate
```

**Then install dependencies and run:**
```bash
pip install -r requirements.txt
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

**To deactivate the virtual environment when done:**
```bash
deactivate
```

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Endpoints

### GET /
Health check endpoint.

### POST /recommend
Accepts: `{ "query": "user's text input" }`

Returns:
```json
{
  "recommended_product": "P123",
  "product_name": "Modern Comfort Sofa",
  "explanation": "We recommend this based on your query: '...'. Real AI will use vector search soon!",
  "confidence": 0.85
}
```

## Notes

- CORS enabled for `http://localhost:3000` and `http://localhost:3001`
- No database, no auth (placeholder for future AI implementation)
- Real AI logic (Qdrant, embeddings) will be added later
