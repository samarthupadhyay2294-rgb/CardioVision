# CardioVision

**Heart Report Analysis & Cardiovascular Risk Assessment**

Production-ready AI healthcare SaaS: upload cardiac reports (PDF/images), OCR extraction, XGBoost ensemble risk scoring, SHAP explainability, personalized recommendations, and PDF reports.

## Guest-first flow

Guests can upload, analyze, view results, and download PDFs **without an account**. Registered users get history, trends, and dashboard analytics.

## Stack

| Layer | Technology |
|-------|------------|
| Frontend | Next.js 15, TypeScript, Tailwind, Framer Motion, Recharts, TanStack Query, Zustand |
| Backend | FastAPI, SQLAlchemy, JWT, Google OAuth |
| ML | XGBoost + LightGBM ensemble, SHAP, your `heart_disease_data_enhanced.csv` |
| OCR | PaddleOCR (EasyOCR fallback) |
| PDF | ReportLab |
| DB | PostgreSQL (SQLite for local dev) |

## Quick start

### 1. Train the model

```bash
cd cardiovision
pip install -r backend/requirements.txt
python scripts/train_model.py
```

### 2. Run API

```bash
cd cardiovision
uvicorn backend.main:app --reload --port 8000
```

### 3. Run frontend

```bash
cd cardiovision/frontend
cp .env.local.example .env.local   # or set NEXT_PUBLIC_API_URL=http://localhost:8000
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000).

### Docker

```bash
docker compose up --build
```

## Environment

Copy `.env.example` to `.env` in the `cardiovision` folder. For production:

- Set `SECRET_KEY`, `DATABASE_URL` (Supabase PostgreSQL)
- Configure `SUPABASE_URL` / `SUPABASE_KEY` for cloud storage
- Set `GOOGLE_CLIENT_ID` for OAuth
- Deploy frontend to **Vercel**, API to **Render**

## API endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/api/auth/register` | Register |
| POST | `/api/auth/login` | Login |
| POST | `/api/auth/google` | Google OAuth |
| POST | `/api/auth/guest-session` | Guest session |
| POST | `/api/upload` | Upload report |
| POST | `/api/analyze/{id}` | Run full pipeline |
| POST | `/api/pipeline` | Upload + analyze |
| GET | `/api/report/{id}` | Get results |
| GET | `/api/pdf/{id}` | Download PDF |
| GET | `/api/history` | User history (auth) |
| GET | `/api/dashboard` | Dashboard (auth) |
| GET | `/api/admin/overview` | Admin stats |

## Admin user

Create a user via `/api/auth/register`, then set `is_admin = true` in the database.

## Disclaimer

CardioVision provides AI-generated cardiovascular risk assessments and is **not** a medical diagnosis. Consult a qualified healthcare professional.

## License

MIT
