# SmartQueue Customer App

Customer-only frontend for the supplied FastAPI Intelligent Queue Management backend.

## Backend
Run the existing backend on:
http://127.0.0.1:8000

Example:
```bash
uvicorn main:app --reload
```

## Frontend
Open `frontend/index.html` in a browser.

For a smoother local run, use VS Code Live Server or:
```bash
cd frontend
python -m http.server 5500
```
Then open:
http://127.0.0.1:5500

## API flow
1. POST `/customers`
2. POST `/queue`
3. GET `/queue/{queue_id}` for status refresh

The frontend does not modify the backend.
