from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="Furniverse AI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RecommendRequest(BaseModel):
    query: str


@app.get("/")
def health_check():
    return {"status": "healthy", "message": "Furniverse AI API is running"}


@app.post("/recommend")
def recommend(request: RecommendRequest):
    return {
        "recommended_product": "P123",
        "product_name": "Modern Comfort Sofa",
        "explanation": f"We recommend this based on your query: '{request.query}'. Real AI will use vector search soon!",
        "confidence": 0.85
    }
