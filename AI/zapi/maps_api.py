import os
import requests
from dotenv import load_dotenv

load_dotenv()

SERPAPI_KEY = os.getenv("GOOGLE_MAPS_API_KEY") or os.getenv("SERPAPI_KEY")


def get_distance(origin: str, destination: str):
    """
    Returns driving distance and duration between two places using SerpAPI Google Maps.
    Example: origin="Hyderabad airport", destination="Charminar"
    """

    url = "https://serpapi.com/search"

    params = {
        "engine": "google_maps",
        "type": "distance_matrix",
        "origins": origin,
        "destinations": destination,
        "api_key": SERPAPI_KEY,
    }

    from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3), retry=retry_if_exception_type(requests.exceptions.RequestException))
    def _call_maps(url, params):
        resp = requests.get(url, params=params, timeout=15)
        if resp.status_code != 200:
            raise requests.exceptions.RequestException(f"HTTP {resp.status_code}")
        return resp.json()

    try:
        data = _call_maps(url, params)

        row = (data.get("distance_matrix", {})
                    .get("rows", [{}])[0]
                    .get("elements", [{}])[0])

        distance = row.get("distance", {}).get("text")
        duration = row.get("duration", {}).get("text")

        return {
            "origin": origin,
            "destination": destination,
            "distance": distance,
            "duration": duration,
        }

    except Exception as e:
        return {"error": f"Could not fetch distance: {e}"}
