# TravelAI — FastAPI backend

Quick setup & run instructions for the `AI/` service.

## Install

Create a virtualenv and install requirements:

```bash
python -m venv .venv
.\.venv\Scripts\activate    # Windows
# or
source .venv/bin/activate     # macOS / Linux

pip install -r requirements.txt
```

## Environment

Create a `.env` file (see `.env.example` or the existing `.env`) and set keys such as:

- `GROQ_API_KEY` (required for Groq LLM)
- `OPENWEATHER_API_KEY` (optional — weather)
- `SERPAPI_KEY` (optional — flights/hotels/tripadvisor)

**Security note:** Do not commit `.env` to source control.

## Run (development)

Run the API with uvicorn from the `AI/` folder:

```bash
uvicorn api:app --reload --port 8001 --host 127.0.0.1
```

### Example endpoints

- Health: `GET http://127.0.0.1:8001/`
- Chat (non-streaming): `POST /chat` with JSON `{ "message": "hello" }`
- Chat (streaming): `POST /chat/stream` with JSON `{ "message": "hello" }` (returns streaming text)
- Trip planner: `POST /trip` with JSON body matching `TripRequest` model

## Notes & Known Issues

- Ensure Python 3.10+ is used to support modern typing and some syntax; some files were updated to be compatible with 3.9 where possible.
- The RAG engine uses `faiss` and `sentence-transformers` which can be heavy to install on some platforms.
- LLM calls require valid API keys set in `.env`.

If you want, I can add tests and a quick `make` script to accelerate local setup.
