# EduCare - AI-Based Dropout Prediction and Counselling System

## Overview
EduCare is a Flask web application for early dropout-risk identification and guided intervention support.
It combines role-based workflows (admin, teacher, student), ML prediction, alerting, counselling, interventions, gamification, and a student-scoped chatbot.

## Current Status
- Core app architecture is modularized (routes, controllers, services, repositories, models).
- Authentication and role-based access control are active.
- Student, teacher, and admin dashboards are available.
- Prediction flow is persisted and explainable (SHAP/LIME metadata).
- Alert, intervention, counselling, and gamification modules are integrated.
- Chatbot has been migrated to a service-layer RAG scaffold with Chroma.

## Major Features

### 1. Prediction and Explainability
- Dropout risk prediction from student profile signals.
- Stored predictions with category and top contributing factors.
- Explainability outputs include SHAP/LIME details.

### 2. Alerts and Interventions
- Alert generation and de-duplication safeguards.
- Intervention creation and assignment workflow.
- Teacher/admin access controls for student detail and intervention-related operations.

### 3. Counselling and Gamification
- Counselling request and counselling log support.
- Gamification profile, points, badges, and leaderboard views.

### 4. Chatbot (Current Architecture)
- Chat endpoint support:
   - POST /chat (frontend compatibility route)
   - POST /api/chatbot (API route, student-only)
- Service-layer chatbot pipeline under app/services/chatbot.
- Student-scoped RAG context built from profile, risk, alerts, interventions, and counselling logs.
- Chroma persistence configured to instance/chroma_db.
- Quick-intent handling includes profile, risk, weak topics, monthly plan, and crisis-first routing.

## Tech Stack
- Backend: Flask 3.0.0, Flask-Login, SQLAlchemy 2.0.23
- Database: PostgreSQL
- ML/Data: scikit-learn, SHAP, pandas, numpy
- Frontend: Jinja templates, Bootstrap 5, Chart.js
- RAG/LLM: LangChain 0.3.x, Chroma, sentence-transformers, Groq

## Repository Structure (Current)
```text
capstone/
|-- run.py
|-- requirements.txt
|-- dataset.csv
|-- app/
|   |-- __init__.py
|   |-- config.py
|   |-- controllers/
|   |-- routes/
|   |-- services/
|   |   |-- chatbot/
|   |-- repositories/
|   |-- models/
|   |-- ml/
|   |-- templates/
|   |-- static/
|-- scripts/
|   |-- functional_smoke_test.py
|   |-- functional_policy_checks.py
|   |-- functional_prediction_checks.py
|-- docs/
|-- instance/
```

## Setup

### Prerequisites
- Python 3.11+
- PostgreSQL

### 1. Create and activate virtual environment
```bash
python -m venv venv
venv\Scripts\activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure environment variables
Create a .env file in project root:

```env
SECRET_KEY=change-this

DB_USER=postgres
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432
DB_NAME=student_counselling_db

GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3

CHROMA_PERSIST_DIR=instance/chroma_db
CHROMA_COLLECTION_PREFIX=student_chatbot
```

Notes:
- If GROQ_MODEL is unset, the app default is llama-3.3-70b-versatile.
- Chatbot retrieval data is persisted under instance/chroma_db.

### 4. Create database and seed data
```bash
set FLASK_APP=run.py
flask db-create
flask seed-db
flask seed-users
```

### 5. Train ML model (if needed)
```bash
python app/ml/train_model.py
```

### 6. Run application (local)
```bash
python run.py
```

Open http://127.0.0.1:5000

### 7. Deploy on Railway (Docker)
This repository is now deployment-ready for Railway with:
- `Dockerfile`
- `.dockerignore`
- `railway.json`
- `wsgi.py` (production app entry)

Required Railway environment variables:
```env
SECRET_KEY=change-this
DATABASE_URL=postgresql://...
GROQ_API_KEY=...
GROQ_MODEL=llama-3.3-70b-versatile
GROQ_TEMPERATURE=0.3
```

Alternative (if DATABASE_URL is not used):
```env
DB_USER=...
DB_PASSWORD=...
DB_HOST=...
DB_PORT=5432
DB_NAME=...
```

Recommended for persistent chatbot vector store:
```env
CHROMA_PERSIST_DIR=/data/chroma_db
```
Attach a Railway volume at `/data` if you want Chroma persistence across deploys.

Deployment steps:
1. Push this repo to GitHub.
2. In Railway, create a new project from the GitHub repo.
3. Railway auto-detects `Dockerfile` and builds the service.
4. Add the environment variables in Railway project settings.
5. Provision PostgreSQL in Railway (or use external Postgres) and wire DB vars.
6. Trigger deploy; Railway injects `PORT` automatically.

## Default Role Notes
- Student:
   - Can access own dashboard and own prediction data.
   - Can use chatbot endpoint.
   - Cannot access other students' predictions or restricted pages.
- Teacher:
   - Can access teacher dashboard.
   - Prediction access is limited to actively assigned students.
- Admin/Counselor:
   - Elevated access for management workflows.

## Validation Scripts
Run these after major changes:

```bash
python scripts/functional_smoke_test.py
python scripts/functional_policy_checks.py
python scripts/functional_prediction_checks.py
```

Latest known regression status in project notes:
- Smoke: 22 passed
- Policy: 5 passed
- Prediction: 11 passed

## API Endpoints (Key)
- POST /api/predict/<student_id>
- POST /api/chatbot
- POST /chat

## Known Next Enhancements
- Crisis escalation workflow: notify assigned teacher for dangerous intent.
- Continue chatbot quality improvements for richer personalized guidance.
- Complete final deployment documentation and evaluator checklist.

## License
Educational project.
