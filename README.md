# AikApply

AI-assisted university admissions for Pakistani students. Fill one application form, get AI university recommendations, track deadlines, and let the system auto-fill admission portals for you.

## Features

- **One application form** — personal, family, academic details and documents, reused everywhere (view and edit any time).
- **AI University Recommender** — Gemini recommends universities from your preferred fields, marks, budget and location; pre-filled from your application, with PDF export.
- **Auto-apply** — Selenium scrapes a university portal, Gemini maps your data onto its fields, and a browser fills and submits the form (single-page, multi-step and login-protected portals), with screenshots.
- **Deadline tracker** — universities and deadlines loaded from an Excel file by admins, with urgency levels.
- **AI chatbot** — career and university guidance.
- **Admin controls** — only staff accounts can upload, edit or delete university data.

## Project structure

```
backend-fyp/aikapply/   Django REST API (accounts, student_data, recommendations,
                        automation_pipline, deadline, dummy_university demo portals)
fyp-frontend1/          React + Vite + Tailwind frontend
```

## Running locally

### Backend

```bash
cd backend-fyp/aikapply
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env          # then add your GEMINI_API_KEY
python manage.py migrate
python manage.py createsuperuser   # admin account for managing universities
python manage.py runserver 127.0.0.1:8000
```

Auto-apply needs Google Chrome installed.

### Frontend

```bash
cd fyp-frontend1
npm install
npm run dev                   # http://127.0.0.1:5173
```

## Trying auto-apply with the demo portals

The backend serves four demo university portals at `http://127.0.0.1:8000/demo-portals/<name>/`:

| Portal | Tests |
|---|---|
| `air-university` | Single-page form |
| `uet-lahore` | Multi-step form with Next buttons |
| `fast-nuces` | Login first (`student` / `au2024`) |
| `bahria` | Unusual field names |

`universities_deadlines.xlsx` lists these portals. Sign in as an admin and upload it from the dashboard (or it is imported automatically on first start). Submissions received by the demo portals are listed at `http://127.0.0.1:8000/demo-portals/submissions/`.

> The Gemini free tier allows about 5 requests per minute, shared by the recommender, chatbot and auto-apply.

## Deployment (Hugging Face Spaces + Neon)

The `Dockerfile` builds one container: the React app, the Django API (gunicorn + WhiteNoise) and headless Chromium for auto-apply. Data is stored in Postgres via `DATABASE_URL`.

1. Add to `backend-fyp/aikapply/.env`: `HF_TOKEN` (Hugging Face write token) and `DATABASE_URL` (e.g. a free Neon Postgres connection string).
2. Commit your changes, then run:

   ```bash
   backend-fyp/aikapply/venv/bin/python deploy/deploy_hf.py
   ```

The script creates the Space, sets its secrets and uploads the committed code; Hugging Face builds and starts the container. Uploaded files (photos, documents, screenshots) are not persistent on the free tier.
