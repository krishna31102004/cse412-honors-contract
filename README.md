Orders Demo Setup
=================

Prerequisites
-------------
- Python 3.12+
- Node.js 18+
- PostgreSQL running locally

1. SQL Setup
------------
```bash
psql postgres -c "CREATE DATABASE orders;"
psql orders -f sql/schema.sql
```

2. Data generation and load
---------------------------
```bash
python3 -m venv .venv-data
source .venv-data/bin/activate
pip install Faker
python generate_data.py
python load_data.py
deactivate
```

3. Start the backend (FastAPI)
------------------------------
```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```
API docs: http://127.0.0.1:8000/docs

4. Start the frontend (React)
----------------------------
```bash
cd frontend
npm install
cp .env.example .env
npm run dev
```
Open the printed Vite URL (default http://localhost:5173) to use the UI.
