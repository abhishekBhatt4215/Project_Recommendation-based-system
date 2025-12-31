import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("SERPAPI_KEY")


def search_tripadvisor(
    city: str,
    interests: str | None = None,
    max_results: int = 10,
    currency: str = "INR",
):
    """
    Uses SerpAPI's Tripadvisor Search Engine Results API.

    city      : e.g. "Hyderabad", "Goa", "Manali"
    interests : e.g. "food", "nightlife", "family activities", "adventure", "romantic"

    Returns:
        {
          "places": [
            {
              "title": ...,
              "category": ...,
              "rating": ...,
              "reviews": ...,
              "price_level": ...,
              "address": ...,
              "snippet": ...,
              "image": ...,
              "link": ...
            },
            ...
          ]
        }
    """

    if not SERPAPI_KEY:
        return {"error": "SERPAPI_KEY missing in .env"}

    # Build query like: "Hyderabad best food and nightlife" etc.
    if interests:
        query = f"{city} {interests}"
    else:
        query = city

    url = "https://serpapi.com/search"

    params = {
        "engine": "tripadvisor",  # <-- IMPORTANT: Tripadvisor Search Engine on SerpAPI
        "q": query,
        "currency": currency,
        "hl": "en",
        "api_key": SERPAPI_KEY,
    }

    from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def _call_tripadvisor(url, params):
        resp = requests.get(url, params=params, timeout=20)
        if resp.status_code != 200:
            raise requests.exceptions.RequestException(f"HTTP {resp.status_code}")
        return resp.json()

    try:
        data = _call_tripadvisor(url, params)

        # Common SerpAPI Tripadvisor format: "organic_results"
        results = data.get("organic_results", []) or data.get("results", [])

        places = []

        for r in results[:max_results]:
            title = r.get("title")
            category = r.get("category") or r.get("type")
            rating = r.get("rating")
            reviews = r.get("reviews")
            price_level = r.get("price_level")
            address = r.get("address")
            snippet = r.get("snippet") or r.get("description")
            image = r.get("thumbnail")
            link = r.get("link")

            places.append(
                {
                    "title": title,
                    "category": category,         # e.g. "Restaurant", "Attraction"
                    "rating": rating,
                    "reviews": reviews,
                    "price_level": price_level,   # $, $$, ₹₹, etc.
                    "address": address,
                    "snippet": snippet,
                    "image": image,
                    "link": link,
                }
            )

        if not places:
            return {"error": "No Tripadvisor places found", "raw": data}

        return {"places": places}

    except Exception as e:
        return {"error": f"Exception calling SerpAPI Tripadvisor API: {e}"}
