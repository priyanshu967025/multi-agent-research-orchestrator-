# 🚀 Production Deployment Guide — Multi-Agent Research Orchestrator

Complete production deployment guide for hosting the **Auth-First Multi-Agent Research Orchestrator** on cloud infrastructure (Render, Railway, Vercel, Docker Compose, and AWS).

---

## 🏗️ Architecture & Component Overview

```
                        ┌─────────────────────────────────────────────────────────────┐
                        │                STREAMLIT FRONTEND APP                       │
                        │           (Render / Railway / Streamlit Cloud)             │
                        └──────────────────────────────┬──────────────────────────────┘
                                                       │
                                           Token Authenticated REST API
                                                       │
                        ┌──────────────────────────────▼──────────────────────────────┐
                        │             DJANGO REST API BACKEND                         │
                        │            (Render / Railway / AWS EC2)                     │
                        └──────────────┬──────────────────────────────┬───────────────┘
                                       │                              │
                        ┌──────────────▼──────────────┐ ┌─────────────▼───────────────┐
                        │   PERSISTENT DATABASE       │ │   VECTOR STORE (RAG)        │
                        │ (PostgreSQL / SQLite /      │ │   (ChromaDB / Pinecone /    │
                        │  MongoDB via Djongo)        │ │    Qdrant)                  │
                        └─────────────────────────────┘ └─────────────────────────────┘
```

---

## 1. Database Choice & Configuration

The application uses Django ORM which supports multiple database engines out-of-the-box:

### Option A: PostgreSQL (Recommended for Production)
In `django_backend/django_backend/settings.py`, configure:
```python
import dj_database_url

DATABASES = {
    'default': dj_database_url.config(
        default=os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')),
        conn_max_age=600
    )
}
```

### Option B: MongoDB (Alternative Document Store)
If MongoDB is preferred, use `djongo` as the database engine in `settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'djongo',
        'NAME': 'research_orchestrator_db',
        'CLIENT': {
            'host': os.getenv('MONGODB_URI', 'mongodb://localhost:27017/research_orchestrator_db'),
        }
    }
}
```

---

## 2. Cloud Platform Deployment Steps

### Method 1: Render Deployment (Recommended Dual-Service)

1. **Deploy Django REST API Backend (Web Service)**:
   - **Repository**: Connect your GitHub repository.
   - **Environment**: Python 3.12
   - **Build Command**: `pip install -r requirements.txt && python django_backend/manage.py migrate`
   - **Start Command**: `gunicorn django_backend.django_backend.wsgi:application --bind 0.0.0.0:$PORT`
   - **Environment Variables**:
     ```env
     GROQ_API_KEY=your_groq_api_key
     TAVILY_API_KEY=your_tavily_api_key
     DJANGO_SECRET_KEY=your_random_production_secret
     ```

2. **Deploy Streamlit Frontend (Web Service)**:
   - **Environment**: Python 3.12
   - **Start Command**: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Environment Variables**: Set `DJANGO_API_URL` to your live backend domain (e.g. `https://your-backend.onrender.com/api/v1`).

---

### Method 2: Railway Deployment

1. Click **New Project** -> **Deploy from GitHub repo**.
2. Add a **PostgreSQL Database** plugin.
3. Railway automatically injects `DATABASE_URL`.
4. Deploy the root directory with start command:
   ```bash
   python django_backend/manage.py migrate && gunicorn django_backend.django_backend.wsgi:application & streamlit run app.py --server.port 8501
   ```

---

### Method 3: Containerized Docker Compose Setup

Run both frontend and backend on any cloud VPS (AWS EC2, DigitalOcean, Hetzner):

```bash
# Clone and build containers
git clone https://github.com/your-username/multi-agent-research-orchestrator.git
cd multi-agent-research-orchestrator
cp .env.example .env

# Build and start background containers
docker-compose up -d --build
```

Access:
- **Streamlit App**: `http://<your-server-ip>:8501`
- **Django REST API**: `http://<your-server-ip>:8000/api/v1/`

---

## 3. Production Security Guidelines

1. **Authentication Token Scope**: Every request requires `Authorization: Token <key>` header.
2. **CORS Restrictions**: Update `CORS_ALLOW_ALL_ORIGINS = False` in `django_backend/settings.py` and set `CORS_ALLOWED_ORIGINS` to your Streamlit frontend domain.
3. **Environment Security**: Keep `DEBUG = False` in production.
