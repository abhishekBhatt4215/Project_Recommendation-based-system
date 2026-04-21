# AI-Based Travel Recommendation System

An AI-powered web application that generates personalized travel 
itineraries based on user preferences, budget, and constraints 
using a RAG (Retrieval-Augmented Generation) based AI service.

## Tech Stack
- **Backend:** Python, Django, Django REST Framework
- **Frontend:** React.js, Tailwind CSS
- **AI Service:** Python, FastAPI, Uvicorn (RAG-based engine)
- **Database:** MySQL
- **Auth:** JWT Authentication

## Project Structure
├── AI/              # RAG-based AI recommendation engine
├── backend/         # Django REST API server
├── frontend/        # React + Tailwind frontend
└── data/            # Dataset files

## Features
- Personalized travel recommendations using RAG-based AI engine
- Constraint-based filtering (budget, destination, duration)
- JWT-secured API endpoints with Role-Based Access Control
- Recommendation history tracking
- Agent-based query routing for intelligent responses

## How to Run

Open 3 terminals:

**Terminal 1 — Django Backend**
```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

**Terminal 2 — Frontend**
```bash
cd frontend
npm install
npm run dev
```

**Terminal 3 — AI Service**
```bash
cd AI
pip install -r requirements.txt
uvicorn api:app --reload
```
