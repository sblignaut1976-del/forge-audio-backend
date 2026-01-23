# Forge Audio Backend

FastAPI backend for stem separation application.

## Tech Stack
- FastAPI
- SQLAlchemy + PostgreSQL (Supabase)
- Pydantic
- Librosa
- Docker

## Setup
1. `python3 -m venv venv`
2. `source venv/bin/activate`
3. `pip install -r requirements.txt`
4. `cp .env.example .env` (Update with your credentials)
5. `uvicorn app.main:app --reload`

## API Documentation
Once running, visit `http://localhost:8000/docs` for interactive Swagger docs.
