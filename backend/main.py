from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import os
import json
import requests
from datetime import datetime, timezone
from dotenv import load_dotenv
from agent import chat
from flowise import get_flowise_memory, query_nutrition_architect, query_life_os, query_daily_briefing
import anthropic
from config import ANTHROPIC_API_KEY

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

SECRET_USERNAME = os.getenv("RUBY_USERNAME", "")
SECRET_PASSWORD = os.getenv("RUBY_PASSWORD", "")
SECRET_TOKEN = os.getenv("RUBY_SECRET_TOKEN", "")

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

class ContractRequest(BaseModel):
    document_text: str
    filename: Optional[str] = None
    question: Optional[str] = None

class TTSRequest(BaseModel):
    text: str

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

@app.get("/api/calendar/today")
async def calendar_today_endpoint():
    try:
        creds = None
        sa_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        token_json = os.getenv("GOOGLE_CALENDAR_TOKEN_JSON")

        if sa_json:
            from google.oauth2 import service_account
            info = json.loads(sa_json)
            creds = service_account.Credentials.from_service_account_info(
                info,
                scopes=["https://www.googleapis.com/auth/calendar.readonly"],
            )
        elif token_json:
            from google.oauth2.credentials import Credentials
            import google.auth.transport.requests
            creds = Credentials.from_authorized_user_info(json.loads(token_json))
            if creds.expired or not creds.valid:
                try:
                    creds.refresh(google.auth.transport.requests.Request())
                except Exception:
                    return []
        else:
            return []

        from googleapiclient.discovery import build
        service = build("calendar", "v3", credentials=creds)

        calendar_id = os.getenv("GOOGLE_CALENDAR_ID", "primary")
        from zoneinfo import ZoneInfo
        melb_tz = ZoneInfo("Australia/Melbourne")
        now_melb = datetime.now(melb_tz)
        day_start = now_melb.replace(hour=0, minute=0, second=0, microsecond=0).isoformat()
        day_end = now_melb.replace(hour=23, minute=59, second=59, microsecond=0).isoformat()

        result = service.events().list(
            calendarId=calendar_id,
            timeMin=day_start,
            timeMax=day_end,
            singleEvents=True,
            orderBy="startTime",
            maxResults=20,
        ).execute()

        events = []
        for item in result.get("items", []):
            start_raw = item["start"].get("dateTime") or (item["start"].get("date", "") + "T00:00:00Z")
            end_raw = item["end"].get("dateTime") or (item["end"].get("date", "") + "T23:59:59Z")
            events.append({
                "id": item["id"],
                "title": item.get("summary", "(No title)"),
                "start": start_raw,
                "end": end_raw,
            })

        return events
    except Exception:
        return []


@app.post("/api/contract")
async def contract_endpoint(req: ContractRequest):
    try:
        _contract_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        if req.question:
            user_message = f"Question: {req.question}\n\nContract document:\n{req.document_text}"
        else:
            user_message = f"Please provide a full analysis of the following contract document:\n\n{req.document_text}"

        if req.filename:
            user_message = f"Filename: {req.filename}\n\n{user_message}"

        with _contract_client.messages.stream(
            model="claude-opus-4-6",
            max_tokens=8192,
            system=(
                "You are an expert contract lawyer and legal analyst with decades of experience "
                "reviewing commercial, employment, real estate, and general legal agreements. "
                "You provide clear, accurate, and thorough analysis of contracts and legal documents. "
                "When asked a specific question, answer it directly and precisely with reference to the "
                "relevant clauses. When performing a full analysis (no specific question), structure your "
                "response with the following sections:\n\n"
                "1. **Key Parties** — Identify all parties and their roles\n"
                "2. **Core Obligations** — What each party must do\n"
                "3. **Important Dates & Deadlines** — Any time-sensitive provisions\n"
                "4. **Risks & Red Flags** — Unfair terms, unusual clauses, or areas of concern\n"
                "5. **Termination Clauses** — How and when the agreement can be ended\n"
                "6. **Plain English Summary** — A concise, jargon-free overview of the whole document\n\n"
                "Be direct and practical. Flag anything the reader should pay close attention to before signing."
            ),
            messages=[{"role": "user", "content": user_message}]
        ) as stream:
            response = stream.get_final_message().content[0].text
        return {"response": response}
    except Exception as e:
        return {"error": str(e)}

@app.post("/api/tts")
async def tts_endpoint(req: TTSRequest):
    api_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID")
    if not api_key or not voice_id:
        raise HTTPException(status_code=500, detail="ElevenLabs credentials not configured")

    response = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
        headers={
            "xi-api-key": api_key,
            "Content-Type": "application/json",
        },
        json={
            "text": req.text,
            "model_id": "eleven_turbo_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
            },
        },
        stream=True,
        timeout=30,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=f"ElevenLabs error: {response.text}")

    return StreamingResponse(response.iter_content(chunk_size=4096), media_type="audio/mpeg")


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
