# Hardening & Testing Guide — TravelAI

This file explains how to test the recent hardening changes (validation, timeouts/retries, and consistent errors).

## 1) Install/update dependencies

From the `AI/` folder, install updated requirements:

```bash
pip install -r requirements.txt
# or if you're using the project-level venv
pip install tenacity
```

## 2) Run the API locally

```bash
uvicorn api:app --reload --port 8001
```

## 3) Test input validation

- Valid trip request (should return itinerary or a message):

```bash
curl -X POST "http://localhost:8001/trip" -H "Content-Type: application/json" -d \
'{"origin_city":"Delhi","destination_city":"Goa","depart_date":"2025-12-10","return_date":"2025-12-12","passengers":2}'
```

- Invalid cabin_class (should return 422 validation error):

```bash
curl -X POST "http://localhost:8001/trip" -H "Content-Type: application/json" -d \
'{"origin_city":"Delhi","destination_city":"Goa","depart_date":"2025-12-10","return_date":"2025-12-12","cabin_class":"rocket"}'
```

- Invalid date format (should return 422):

```bash
curl -X POST "http://localhost:8001/trip" -H "Content-Type: application/json" -d \
'{"origin_city":"Delhi","destination_city":"Goa","depart_date":"10-12-2025","return_date":"12-12-2025"}'
```

Our validators accept `YYYY-MM-DD` and `DD-MM-YYYY` (converted to YYYY-MM-DD internally).

## 4) Test timeouts and retries

The external API wrappers (weather, flights, hotels, maps, Tripadvisor) now use a `requests` timeout and `tenacity` retry decorator.

- To simulate transient network errors, either:
  - Temporarily block network to a service and call the /trip endpoint, or
  - Introduce a short invalid key in `.env` to get a non-200 and observe retry behavior in logs.

In case of transient failures the wrapper will retry 3 times with exponential backoff.

## 5) Run automated tests (new)

We added basic automated tests to help you get quick confidence:

- Django (management command import) tests:

  Run from the Django project root:

  ```powershell
  Set-Location 'C:\Users\Abhishek\OneDrive\Desktop\recommendation_project\backend\travel_recommendation'
  .\manage.py test recommendations
  ```

- FastAPI tests (pytest):

  Run from the project root (pytest is installed in the AI requirements):

  ```powershell
  Set-Location 'C:\Users\Abhishek\OneDrive\Desktop\recommendation_project'
  pytest AI/tests/test_api_endpoints.py -q
  ```

These tests mock the `agent` in the FastAPI app and verify validation, streaming, and error handling.

## 6) Test streaming and error handling

- Chat streaming endpoint:

```bash
curl -X POST "http://localhost:8001/chat/stream" -H "Content-Type: application/json" -d '{"message":"Hello"}'
```

The endpoint now yields stream chunks; if the LLM fails, the stream ends with a final `"[ERROR] ..."` token.

## 6) Logging

Basic logging is configured (`INFO` level). Check the console for logged exceptions and messages.

## 7) Notes & next steps

- For production/long-term hardening, add rate-limiting, authentication, structured logs, monitoring and health checks.
- Consider mocking external APIs in unit tests to check retry behavior deterministically (use `responses` or `requests-mock`).
- If you want, I can add `pytest` tests for timeout and validation behavior.
