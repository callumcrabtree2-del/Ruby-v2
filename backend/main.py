from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from agent import chat
from flowise import get_flowise_memory, query_nutrition_architect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_media_type: Optional[str] = None

class NutritionRequest(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_media_type: Optional[str] = None

@app.get("/")
def root():
    return {"status": "Ruby AI Backend is running"}

@app.post("/api/chat")
async def chat_endpoint(req: ChatRequest):
    try:
        response = chat(
            req.message,
            image_data=req.image_data,
            image_media_type=req.image_media_type
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/nutrition")
async def nutrition_endpoint(req: NutritionRequest):
    try:
        response = query_nutrition_architect(
            req.message,
            image_data=req.image_data,
            image_media_type=req.image_media_type
        )
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}
