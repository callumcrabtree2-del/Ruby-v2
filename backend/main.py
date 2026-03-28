from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import requests
from dotenv import load_dotenv
from agent import chat
from flowise import get_flowise_memory, query_nutrition_architect, query_life_os, query_daily_briefing

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://ruby-v2-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_USERNAME = "Callumc.user"
SECRET_PASSWORD = "Polarbear_24"
SECRET_TOKEN = "ruby-secret-token-2026"

class LoginRequest(BaseModel):
    username: str
    password: str

class ChatRequest(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_media_type: Optional[str] = None

class NutritionRequest(BaseModel):
    message: str
    image_data: Optional[str] = None
    image_media_type: Optional[str] = None

class LifeOSRequest(BaseModel):
    message: str

@app.get("/")
def root():
    return {"status": "Ruby AI Backend is running"}

@app.post("/api/auth/login")
async def login(req: LoginRequest):
    if req.username == SECRET_USERNAME and req.password == SECRET_PASSWORD:
        return {"token": SECRET_TOKEN}
    raise HTTPException(status_code=401, detail="Invalid credentials")

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

@app.post("/api/life-os")
async def life_os_endpoint(req: LifeOSRequest):
    try:
        response = query_life_os(req.message)
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/daily-briefing")
async def daily_briefing_endpoint():
    try:
        response = query_daily_briefing("Good morning, please give me my full daily briefing.")
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/crypto")
async def crypto_endpoint():
    try:
        response = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum,solana&vs_currencies=usd&include_24hr_change=true",
            timeout=10
        )
        data = response.json()
        return {
            "BTC": {"price": data["bitcoin"]["usd"], "change": round(data["bitcoin"]["usd_24h_change"], 2)},
            "ETH": {"price": data["ethereum"]["usd"], "change": round(data["ethereum"]["usd_24h_change"], 2)},
            "SOL": {"price": data["solana"]["usd"], "change": round(data["solana"]["usd_24h_change"], 2)}
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/stocks")
async def stocks_endpoint():
    try:
        stocks = {}
        for symbol in ["NVDA", "AAPL", "MSFT"]:
            response = requests.get(
                f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=2d",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            data = response.json()
            result = data["chart"]["result"][0]
            current = result["meta"]["regularMarketPrice"]
            previous = result["meta"]["chartPreviousClose"]
            change = round(((current - previous) / previous) * 100, 2)
            stocks[symbol] = {"price": round(current, 2), "change": change}
        return stocks
    except Exception as e:
        return {"error": str(e)}

@app.get("/api/weather")
async def weather_endpoint():
    try:
        response = requests.get(
            "https://wttr.in/Melbourne?format=j1",
            timeout=10
        )
        data = response.json()
        current = data["current_condition"][0]
        return {
            "temp": current["temp_C"],
            "feels_like": current["FeelsLikeC"],
            "description": current["weatherDesc"][0]["value"],
            "humidity": current["humidity"]
        }
    except Exception as e:
        return {"error": str(e)}
