# agent_core.py — TravelAI core (stable, CLI-safe)

import os
from typing import Optional
from dotenv import load_dotenv
from groq import Groq

from rag_engine import RAGEngine
from rag_documents import india_travel_docs

from zapi.tools_weather import get_weather
from zapi.flight_api import search_flights_serpapi
from zapi.hotel_api import search_hotels_serpapi
from zapi.tripadvisor_api import search_tripadvisor

# -------------------------------------------------
# ENV
# -------------------------------------------------
load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY missing")

groq_client = Groq(api_key=GROQ_API_KEY)


def call_groq(prompt: str) -> str:
    response = groq_client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2048,
    )
    return response.choices[0].message.content.strip()


# -------------------------------------------------
# TRAVEL AI
# -------------------------------------------------
class TravelAI:
    def __init__(self):
        # ---------- RAG ----------
        self.rag = RAGEngine()
        self.rag.load_docs(india_travel_docs)

    # -------------------------------------------------
    # FULL TRIP PLANNER
    # -------------------------------------------------
    def plan_full_trip(
        self,
        origin_city: str,
        destination_city: str,
        depart_date: str,
        return_date: str,
        passengers: int = 2,
        cabin_class: str = "economy",
        interests: str = "sightseeing",
        days: int = 3,
        max_budget: Optional[int] = None,
    ) -> str:

        # ---------- CITY ALIASES ----------
        CITY_ALIASES = {
            "hyd": "hyderabad",
            "blr": "bangalore",
            "bom": "mumbai",
            "mum": "mumbai",
            "del": "delhi",
            "maa": "chennai",
            "ccu": "kolkata",
        }

        # ---------- STATE → CITY ----------
        STATE_TO_CITY = {
            "kerala": "kochi",
            "tamil nadu": "chennai",
            "karnataka": "bangalore",
            "maharashtra": "mumbai",
            "rajasthan": "jaipur",
            "telangana": "hyderabad",
            "andhra pradesh": "visakhapatnam",
            "west bengal": "kolkata",
        }

        origin_city = origin_city.strip().lower()
        destination_city = destination_city.strip().lower()

        origin_city = CITY_ALIASES.get(origin_city, origin_city)
        destination_city = CITY_ALIASES.get(destination_city, destination_city)

        origin_city = STATE_TO_CITY.get(origin_city, origin_city)
        destination_city = STATE_TO_CITY.get(destination_city, destination_city)

        # ---------- DATE NORMALIZATION ----------
        def normalize_date(d: str) -> str:
            parts = d.split("-")
            if len(parts[0]) == 2:  # DD-MM-YYYY
                return f"{parts[2]}-{parts[1]}-{parts[0]}"
            return d

        depart_date = normalize_date(depart_date)
        return_date = normalize_date(return_date)

        # ---------- CITY → IATA ----------
        CITY_TO_IATA = {
            "delhi": "DEL",
            "hyderabad": "HYD",
            "mumbai": "BOM",
            "bangalore": "BLR",
            "chennai": "MAA",
            "goa": "GOI",
            "kolkata": "CCU",
            "kochi": "COK",
            "trivandrum": "TRV",
            "calicut": "CCJ",
            "jaipur": "JAI",
            "visakhapatnam": "VTZ",
        }

        origin_iata = CITY_TO_IATA.get(origin_city)
        dest_iata = CITY_TO_IATA.get(destination_city)

        if not origin_iata:
            return f"❌ Unsupported origin city: {origin_city.title()}"

        if not dest_iata:
            return f"❌ Unsupported destination city: {destination_city.title()}"

        # ---------- DATA ----------
        weather = get_weather(destination_city)

        flights_raw = search_flights_serpapi(
            origin_airport=origin_iata,
            destination_airport=dest_iata,
            depart_date=depart_date,
            return_date=return_date,
            passengers=passengers,
            cabin_class=cabin_class,
        )
        flights = flights_raw.get("flights", []) if isinstance(flights_raw, dict) else []

        hotels_raw = search_hotels_serpapi(
            city=destination_city,
            checkin=depart_date,
            checkout=return_date,
            adults=passengers,
            rooms=1,
        )
        hotels = hotels_raw.get("hotels", []) if isinstance(hotels_raw, dict) else []

        activities_raw = search_tripadvisor(
            city=destination_city,
            interests="things to do",
            max_results=10,
        )
        activities = activities_raw.get("places", []) if isinstance(activities_raw, dict) else []

        rag_context = self.rag.search(
            f"Travel tips, food, safety, best time for {destination_city}",
            summarize=True,
        )

        budget_text = f"{max_budget} INR" if max_budget else "Not specified"

        prompt = f"""
You are an expert India travel planner.

From: {origin_city.title()}
To: {destination_city.title()}
Depart: {depart_date}
Return: {return_date}
Passengers: {passengers}
Interests: {interests}
Budget: {budget_text}

WEATHER
{weather}

RAG INFO
{rag_context}

FLIGHTS
{flights}

HOTELS
{hotels}

ACTIVITIES
{activities}

OUTPUT:
1. Flights
2. Hotels
3. Day-wise itinerary
4. Transport tips
5. Budget summary
"""

        return call_groq(prompt)

    # -------------------------------------------------
    # 🔥 ITINERARY REFINEMENT (FIXES YOUR ERROR)
    # -------------------------------------------------
    def refine_itinerary(self, existing_itinerary: str, user_request: str) -> str:
        """
        Refines an existing itinerary based on user feedback.
        """

        prompt = f"""
You are an expert India travel planner.

CURRENT ITINERARY:
{existing_itinerary}

USER REQUEST:
{user_request}

INSTRUCTIONS:
- Modify ONLY what the user asked for
- Keep all other days unchanged
- Be realistic and practical
- Return the FULL updated itinerary

UPDATED ITINERARY:
"""
        return call_groq(prompt)
