# Enterprise AI Process Intelligence Engine

Assignment 2 — 100-Process AI Research & Intelligence Engine.

This is a working full-stack application: React frontend, FastAPI backend, SQLite persistence, reusable process-analysis pipeline, research/evidence storage, rankings, and dynamic Process 101 support.

## Run backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn main:app --reload
```

Backend: http://127.0.0.1:8000
API docs: http://127.0.0.1:8000/docs

## Run frontend

In a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Frontend: http://localhost:5173

## Optional local AI

Install Ollama and run:

```bash
ollama pull llama3.2:3b
```

Set `OLLAMA_ENABLED=true` in `backend/.env`.

If Ollama is disabled/unavailable, the application uses a transparent deterministic fallback for development. For the final challenge demo, use a real local model.

## Demo

1. Analyze all seeded processes.
2. View top AI opportunities.
3. Inspect evidence and reasoning.
4. Add a new Process 101.
5. Analyze it using the same endpoint.
6. Refresh and demonstrate persistence.
