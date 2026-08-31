# 🚀 Multi-Agent Research Orchestrator — Deployment Guide

This guide covers deploying MARO across all major cloud providers and production environments.

---

## 🌟 1. Vercel + Render (Recommended Free-Tier Deployment)

### Backend on [Render](https://render.com)
1. Fork or push this repository to GitHub.
2. Go to [Render Dashboard](https://dashboard.render.com/) ➔ **New Web Service**.
3. Select your repository and set:
   - **Build Command**: `pip install -r requirements.txt && cd backend && python manage.py migrate && python manage.py collectstatic --noinput`
   - **Start Command**: `cd backend && gunicorn orchestrator_backend.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --threads 4 --timeout 120`
4. Add Environment Variables:
   - `GROQ_API_KEY`: `your_groq_api_key`
   - `TAVILY_API_KEY`: `your_tavily_api_key`
   - `MODEL_NAME`: `openai/gpt-oss-20b`
   - `DJANGO_DEBUG`: `false`
   - `CORS_ALLOW_ALL_ORIGINS`: `true`

### Frontend on [Vercel](https://vercel.com)
1. Go to [Vercel Dashboard](https://vercel.com/dashboard) ➔ **Add New Project**.
2. Select your repository and choose **Root Directory**: `frontend`.
3. Framework Preset: `Vite`.
4. Set Environment Variable:
   - `VITE_API_URL`: `https://your-backend.onrender.com`
5. Click **Deploy**.

---

## 🐳 2. Docker Compose (Self-Hosted VPS / Droplet)

1. Clone repo onto your Linux server (Ubuntu 22.04+):
   ```bash
   git clone https://github.com/your-username/multi-agent-research-orchestrator.git
   cd multi-agent-research-orchestrator
   ```
2. Create `.env` file with your API keys:
   ```env
   GROQ_API_KEY=your_key
   TAVILY_API_KEY=your_key
   ```
3. Run:
   ```bash
   docker-compose up --build -d
   ```
4. Access:
   - Frontend: `http://<your-server-ip>`
   - Backend API: `http://<your-server-ip>:8000/api/`
