# api.py — FastAPI backend for TravelAI (with CORS)

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime
import logging

from agent_core import TravelAI

# Simple logging config for the AI service; in production use structured logging/central collector
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('travelai')


# Helper to parse ISO date-like strings
def _parse_date(value: str) -> str:
    try:
        # Accept YYYY-MM-DD or DD-MM-YYYY
        if '-' in value:
            parts = value.split('-')
            if len(parts[0]) == 2:  # assume DD-MM-YYYY -> convert
                dt = datetime.strptime(value, '%d-%m-%Y')
            else:
                dt = datetime.strptime(value, '%Y-%m-%d')
            return dt.strftime('%Y-%m-%d')
    except Exception:
        raise ValueError('Invalid date format; expected YYYY-MM-DD or DD-MM-YYYY')
    raise ValueError('Invalid date format')

# -------------------------------------------------
# APP INIT
# -------------------------------------------------
app = FastAPI(
    title="TravelAI",
    version="0.1.0",
    description="Travel AI backend with chat, streaming, and trip planning",
)

# -------------------------------------------------
# CORS (REQUIRED FOR FRONTEND)
# -------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------
# AI AGENT
# -------------------------------------------------
agent = TravelAI()

# -------------------------------------------------
# REQUEST MODELS
# -------------------------------------------------
class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)


class TripRequest(BaseModel):
    origin_city: str = Field(..., min_length=2, max_length=100)
    destination_city: str = Field(..., min_length=2, max_length=100)
    depart_date: str = Field(...)
    return_date: str = Field(...)
    passengers: int = Field(2, ge=1, le=20)
    cabin_class: str = Field("economy")
    interests: Optional[str] = Field("sightseeing", max_length=300)
    days: int = Field(3, ge=1, le=60)
    max_budget: Optional[int] = None

    @validator('cabin_class')
    def cabin_class_choices(cls, v):
        choices = {'economy', 'premium_economy', 'business', 'first'}
        if v not in choices:
            raise ValueError(f"cabin_class must be one of {choices}")
        return v

    @validator('depart_date')
    def depart_date_valid(cls, v):
        return _parse_date(v)

    @validator('return_date')
    def return_date_valid(cls, v):
        return _parse_date(v)

    @validator('destination_city', 'origin_city')
    def strip_city(cls, v):
        return v.strip().lower()


# -------------------------------------------------
# HEALTH
# -------------------------------------------------
@app.get("/")
def health():
    return {"status": "ok", "service": "TravelAI"}


# -------------------------------------------------
# CHAT (NON-STREAMING)
# -------------------------------------------------
@app.post("/chat")
def chat(req: ChatRequest):
    try:
        response = agent.ask(req.message)
        if isinstance(response, str) and response.startswith('[LLM ERROR]'):
            logger.error('LLM error: %s', response)
            raise HTTPException(status_code=503, detail="LLM service error")
        return {"response": response}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('Chat endpoint failed')
        raise HTTPException(status_code=500, detail=str(e))


# -------------------------------------------------
# CHAT (STREAMING)
# -------------------------------------------------
@app.post("/chat/stream")
def chat_stream(req: ChatRequest):
    def generator():
        try:
            for token in agent.ask_stream(req.message):
                yield token
        except Exception as e:
            logger.exception('Streaming chat failed')
            # yield a final error token so clients can react
            yield f"[ERROR] {e}"

    return StreamingResponse(generator(), media_type="text/plain")


# -------------------------------------------------
# FULL TRIP PLANNER
# -------------------------------------------------
@app.post("/trip")
def plan_trip(req: TripRequest):
    try:
        itinerary = agent.plan_full_trip(
            origin_city=req.origin_city,
            destination_city=req.destination_city,
            depart_date=req.depart_date,
            return_date=req.return_date,
            passengers=req.passengers,
            cabin_class=req.cabin_class,
            interests=req.interests,
            days=req.days,
            max_budget=req.max_budget,
        )

        if isinstance(itinerary, str) and itinerary.startswith('❌'):
            # Known validation from agent
            raise HTTPException(status_code=400, detail=itinerary)

        return {"itinerary": itinerary}
    except HTTPException:
        raise
    except Exception as e:
        logger.exception('plan_trip failed')
        raise HTTPException(status_code=500, detail='Trip planning failed')



class RefineRequest(BaseModel):
    itinerary: str
    user_request: str


@app.post("/refine")
def refine_trip(req: RefineRequest):
    updated = agent.refine_itinerary(
        existing_itinerary=req.itinerary,
        user_request=req.user_request,
    )
    return {"itinerary": updated}


