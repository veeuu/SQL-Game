# 🚀 Deployment Guide

## Stack
- **Frontend**: Vercel (React)
- **Backend**: Render (FastAPI)
- **Database**: Neon (PostgreSQL)

All free tiers.

---

## 1️⃣ Database — Neon

1. Go to [neon.tech](https://neon.tech) → Sign up
2. Create project → Copy connection string
3. Update `backend/.env`:
   ```
   PG_HOST=ep-xxx.us-east-1.aws.neon.tech
   PG_PORT=5432
   PG_DB=neondb
   PG_USER=your_user
   PG_PASS=your_password
   ```
4. Run setup:
   ```bash
   cd backend
   python setup_postgres.py
   ```

---

## 2️⃣ Backend — Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect GitHub repo
4. Settings:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
5. Add Environment Variables:
   ```
   PG_HOST=...
   PG_PORT=5432
   PG_DB=...
   PG_USER=...
   PG_PASS=...
   GEMINI_API_KEY=AQ.Ab8RN6KN8Y5sWp_Y8hqDnsyZoapsjtIYzKl03Tp7L8RNuI4WfQ
   GEMINI_MODEL=gemini-3.1-flash-lite-preview
   ```
6. Deploy → Copy URL: `https://your-app.onrender.com`

---

## 3️⃣ Frontend — Vercel

1. Update `frontend/src/.env.production`:
   ```
   REACT_APP_API_URL=https://your-app.onrender.com
   ```
2. Build locally to test:
   ```bash
   cd frontend
   npm run build
   ```
3. Go to [vercel.com](https://vercel.com) → New Project
4. Connect GitHub repo
5. Settings:
   - Root Directory: `frontend`
   - Build Command: `npm run build`
   - Output Directory: `build`
6. Add Environment Variable:
   ```
   REACT_APP_API_URL=https://your-app.onrender.com
   ```
7. Deploy → Get URL: `https://your-app.vercel.app`

---

## 4️⃣ Update CORS

After deploying frontend, update backend CORS in `backend/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://your-app.vercel.app",  # Add your Vercel URL
    ],
    ...
)
```

Redeploy backend on Render.

---

## ✅ Done!

Your app is live at `https://your-app.vercel.app`

---

## Alternative: Single Platform

**Railway** (all-in-one):
- Deploy backend, frontend, and PostgreSQL on one platform
- [railway.app](https://railway.app)
- Free $5/month credit

**Fly.io** (all-in-one):
- Deploy everything with Dockerfiles
- [fly.io](https://fly.io)
- Free tier available
