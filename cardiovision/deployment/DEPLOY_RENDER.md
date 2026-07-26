# Deploy CardioVision on Render

This blueprint deploys:

| Service | Type | URL |
|---------|------|-----|
| **cardiovision-api** | Docker (FastAPI + ML) | `https://cardiovision-api.onrender.com` |
| **cardiovision-web** | Node (Next.js) | `https://cardiovision-web.onrender.com` |
| **cardiovision-db** | PostgreSQL (free) | Internal |

## Prerequisites

1. [Render](https://render.com) account  
2. GitHub repository with this project pushed  

## Option A — Blueprint (recommended)

1. Push your code to GitHub.
2. In Render: **New +** → **Blueprint**.
3. Connect the repository.
4. If your repo root is the **parent** folder (contains `cardiovision/`), Render uses `/render.yaml` at repo root.
5. If your repo root **is** `cardiovision/`, use `cardiovision/render.yaml` or move it to the repo root.
6. Click **Apply**.

After deploy:

1. Open **cardiovision-api** → **Environment**.
2. Set **CORS_ORIGINS** to your frontend URL, e.g.  
   `https://cardiovision-web.onrender.com`  
   (comma-separated if you also use a custom domain).
3. Save — API will redeploy.

The frontend gets **NEXT_PUBLIC_API_URL** automatically from the API service.

## Option B — Manual API only (Docker)

1. **New +** → **Web Service** → connect repo.
2. **Root Directory:** `cardiovision` (if needed).
3. **Runtime:** Docker.
4. **Dockerfile path:** `Dockerfile`.
5. Add **PostgreSQL** from Render dashboard; link `DATABASE_URL`.
6. **Health check path:** `/health`.
7. Env vars:
   - `SECRET_KEY` — generate
   - `DATABASE_URL` — from database
   - `CORS_ORIGINS` — your frontend URL
   - `RENDER` — `true`

## Option C — Frontend on Vercel + API on Render

1. Deploy API on Render (Option B).
2. On Vercel, import `cardiovision/frontend`.
3. Set `NEXT_PUBLIC_API_URL=https://YOUR-API.onrender.com`.
4. Set Render `CORS_ORIGINS` to your Vercel URL.

## Notes

- **Free tier** services spin down after inactivity; first request may take 30–60s.
- **ML model** is trained during the Docker build from `ml_models/datasets/heart_disease_data_enhanced.csv`.
- **PDF text** uses PyMuPDF; scanned PDFs use Poppler (included in Docker image).
- **Disk:** uploads/PDFs on free tier are ephemeral — use Supabase storage env vars for persistence (optional).

## Verify

```bash
curl https://YOUR-API.onrender.com/health
# {"status":"ok","service":"cardiovision-api"}
```

Open the **cardiovision-web** URL and run **Analyze Report**.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Build fails on ML train | Ensure `ml_models/datasets/heart_disease_data_enhanced.csv` is committed |
| CORS error | Set `CORS_ORIGINS` on API to exact frontend URL (https, no trailing slash) |
| 502 on first request | Wait for cold start; check API logs |
| Database error / `could not translate host name "dpg-..."` | Your `DATABASE_URL` points to a missing or expired Postgres instance. In Render: **New + → PostgreSQL** (or open existing `cardiovision-db`), copy **Internal Database URL**, paste into **cardiovision-api → Environment → DATABASE_URL**, save to redeploy. Free databases expire after 90 days of inactivity. |
| Database error (general) | Confirm `DATABASE_URL` uses PostgreSQL from Render (auto-fixed to `postgresql://`) |
