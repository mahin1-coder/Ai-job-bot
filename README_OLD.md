# AI Job Bot — Production-Ready Resume & Job Application Automation

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     REACT DASHBOARD (Port 3000)                 │
│  ┌──────────────┐ ┌───────────────┐ ┌───────────────────────┐   │
│  │ Resume Upload│ │   Job Board   │ │  Application Tracker  │   │
│  │  + Viewer    │ │ Search + Match│ │  + AI Generator       │   │
│  └──────────────┘ └───────────────┘ └───────────────────────┘   │
└────────────────────────────┬────────────────────────────────────┘
                             │ REST API + SSE (streaming)
┌────────────────────────────▼────────────────────────────────────┐
│                  FASTAPI BACKEND (Port 8000)                     │
│                                                                  │
│  Routers: /resumes  /jobs  /applications  /ai                    │
│                                                                  │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────────┐   │
│  │ ResumeParser │ │  JobScraper  │ │      JobMatcher        │   │
│  │ pdfplumber   │ │ Adzuna API   │ │  OpenAI Embeddings     │   │
│  │ PyMuPDF      │ │ RemoteOK API │ │  Cosine Similarity     │   │
│  │ GPT-4o parse │ │              │ │  GPT-4o Explanations   │   │
│  └──────────────┘ └──────────────┘ └────────────────────────┘   │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    AIGeneratorService                    │   │
│  │  Tailored Resume (GPT-4o) │ Cover Letter (GPT-4o)        │   │
│  │  Non-streaming POST       │ SSE Streaming GET            │   │
│  └──────────────────────────────────────────────────────────┘   │
└──────────┬──────────────────────────────────┬───────────────────┘
           │                                  │
┌──────────▼───────────┐          ┌───────────▼─────────────┐
│    PostgreSQL DB      │          │      External APIs       │
│  resumes / jobs       │          │  - OpenAI GPT-4o         │
│  applications         │          │  - OpenAI Embeddings     │
└──────────────────────┘          │  - Adzuna Jobs API       │
                                  │  - RemoteOK API (free)   │
┌─────────────────────┐           └─────────────────────────┘
│      Redis           │
│  API response cache  │
│  Celery task queue   │
└─────────────────────┘
```

## Folder Structure

```
ai-job-bot/
├── backend/
│   ├── app/
│   │   ├── main.py               # FastAPI app + lifespan
│   │   ├── config.py             # Pydantic settings (env vars)
│   │   ├── database.py           # Async SQLAlchemy engine + session
│   │   ├── models/
│   │   │   ├── resume.py         # Resume ORM model
│   │   │   ├── job.py            # Job ORM model
│   │   │   └── application.py    # Application ORM model
│   │   ├── schemas/
│   │   │   ├── resume.py         # Pydantic request/response schemas
│   │   │   ├── job.py
│   │   │   └── application.py
│   │   ├── services/
│   │   │   ├── resume_parser.py  # PDF/DOCX → structured JSON via GPT-4o
│   │   │   ├── job_scraper.py    # Adzuna + RemoteOK API clients
│   │   │   ├── job_matcher.py    # Embedding similarity + GPT-4o match reasons
│   │   │   ├── ai_generator.py   # Tailored resume + cover letter generation
│   │   │   └── application_tracker.py  # Application CRUD
│   │   ├── routers/
│   │   │   ├── resume.py         # Upload, list, get, delete
│   │   │   ├── jobs.py           # Search, match, list
│   │   │   ├── applications.py   # CRUD + status updates
│   │   │   └── ai.py             # Generate + SSE streaming
│   │   └── utils/
│   │       ├── file_utils.py     # Upload validation + safe file saving
│   │       └── text_utils.py     # Text cleaning helpers
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── App.jsx               # Router + nav
│   │   ├── components/
│   │   │   ├── ResumeUpload.jsx  # Drag-drop upload + parsed data view
│   │   │   ├── JobBoard.jsx      # Search + AI match results
│   │   │   ├── ApplicationTracker.jsx  # Kanban-style status tracker
│   │   │   └── AIGenerator.jsx   # Streaming resume + cover letter
│   │   └── services/api.js       # Axios API client
│   ├── package.json
│   ├── vite.config.js
│   └── Dockerfile
├── docker-compose.yml            # Full stack: API + Worker + DB + Redis + Frontend
└── .env.example                  # All required environment variables
```

## Quick Start (Local Development)

### Prerequisites
- Docker & Docker Compose
- OpenAI API key
- (Optional) Free Adzuna API key from https://developer.adzuna.com

### 1. Clone and configure

```bash
git clone <your-repo>
cd ai-job-bot
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### 2. Run with Docker Compose

```bash
docker-compose up --build
```

Services will start at:
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Run backend locally (without Docker)

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
playwright install chromium

# Start PostgreSQL and Redis locally, then:
uvicorn app.main:app --reload --port 8000
```

### 4. Run frontend locally

```bash
cd frontend
npm install
npm run dev
```

---

## Implementation Plan (Step by Step)

### Phase 1 — Core Upload + Parse ✅
1. User uploads resume (PDF/DOCX/TXT) via drag-drop
2. Backend validates file (extension + magic bytes)
3. `ResumeParserService` extracts raw text (pdfplumber → PyMuPDF fallback)
4. GPT-4o structures text into typed JSON (name, skills, experience, education)
5. Saved to PostgreSQL, returned to frontend

### Phase 2 — Job Discovery ✅
1. User enters query + location in Job Board
2. `JobScraperService` calls Adzuna API + RemoteOK concurrently
3. Results deduplicated and saved to DB
4. Display with apply links

### Phase 3 — AI Matching ✅
1. User clicks "AI Match" with a resume selected
2. Backend generates OpenAI embeddings for resume text and all job descriptions
3. Cosine similarity computed for each job → match_score (0–1)
4. Top 5 results enriched with GPT-4o explanation (reasons + missing skills)
5. Results displayed with colour-coded match badges

### Phase 4 — AI Generation ✅
1. User clicks "Generate & Apply" on any job
2. Application record created in DB
3. On AI Generator page: click "Generate Both" or "⚡ Stream"
4. GPT-4o rewrites resume bullets to mirror job description language
5. GPT-4o writes 3-paragraph targeted cover letter
6. Both saved to application record
7. User copies and applies

### Phase 5 — Application Tracking ✅
1. Application Tracker shows all applications
2. Status dropdown: pending → applied → interviewing → offer / rejected
3. Stats dashboard: total, applied, interviewing, offers

---

## API Reference

### Authentication (NEW ✨)
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/v1/auth/register` | Create new user account | No |
| POST | `/api/v1/auth/login` | Login and get JWT tokens | No |
| POST | `/api/v1/auth/refresh` | Refresh access token | No |
| GET | `/api/v1/auth/me` | Get current user profile | Yes |

### Resumes
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/resumes/upload` | Upload + AI-parse resume |
| GET | `/api/v1/resumes/` | List all resumes |

### Jobs & Matching
| GET | `/api/v1/jobs/search?query=...` | Search jobs from APIs |
| POST | `/api/v1/jobs/match/{resume_id}` | AI-rank jobs for resume |
| POST | `/api/v1/applications/` | Create application |
| GET | `/api/v1/applications/` | List all applications |
| GET | `/api/v1/applications/stats` | Dashboard stats |
| PATCH | `/api/v1/applications/{id}/status` | Update status |
| POST | `/api/v1/ai/generate` | Generate resume + cover letter |
| GET | `/api/v1/ai/stream/resume/{id}` | SSE stream: tailored resume |
| GET | `/api/v1/ai/stream/cover-letter/{id}` | SSE stream: cover letter |

Full interactive docs: http://localhost:8000/docs

---

## Technology Choices

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | FastAPI + async | High performance, auto-generated docs, async I/O |
| Database | PostgreSQL + asyncpg | ACID, JSON columns, future pgvector support |
| ORM | SQLAlchemy 2 async | Type-safe, production-tested |
| AI | GPT-4o | Best-in-class instruction following, JSON mode |
| Embeddings | text-embedding-3-small | Fast, cheap, 1536 dimensions |
| PDF Parsing | pdfplumber + PyMuPDF | Handles 99% of real-world PDFs |
| Job APIs | Adzuna + RemoteOK | No ToS violations, free tier available |
| Frontend | React + Vite + Tailwind | Fast dev cycle, minimal bundle |
| Streaming | SSE (Server-Sent Events) | Simple, no WebSocket overhead |
| Queue | Celery + Redis | Background scraping/AI jobs at scale |

---

## Production Features ✅

### Security & Authentication
- ✅ **JWT authentication** with access + refresh tokens
- ✅ **Password hashing** (bcrypt via passlib)
- ✅ **Rate limiting** (200 req/min global, 10 uploads/min per IP)
- ✅ **CORS protection** with configurable origins
- ✅ **Input validation** (file magic bytes, size limits)
- ✅ **Protected routes** via dependency injection

### Database & Migrations
- ✅ **Alembic migrations** (no more `create_all()`)
- ✅ **Async SQLAlchemy** with connection pooling
- ✅ **Database indexes** on frequently queried fields
- ✅ **Foreign key constraints** with CASCADE deletes

### Background Jobs & Scalability
- ✅ **Celery workers** for async job scraping
- ✅ **Celery Beat** for scheduled cleanup tasks
- ✅ **Redis queue** for task distribution
- ✅ **Horizontal scaling** ready (stateless API)

### Testing & CI/CD
- ✅ **pytest test suite** with async support
- ✅ **GitHub Actions pipeline** (lint, test, build, deploy)
- ✅ **Code coverage** reporting (Codecov)
- ✅ **Security scanning** (Trivy)
- ✅ **Docker multi-stage builds** for production

### Deployment & Infrastructure
- ✅ **nginx reverse proxy** with SSL termination
- ✅ **Docker Compose production config**
- ✅ **Health check endpoints**
- ✅ **Structured logging** (JSON via structlog)
- ✅ **Error tracking** (Sentry integration ready)
- ✅ **Environment-based config** (dev/staging/prod)

### Observability
- ✅ **Health checks** for all services
- ✅ **Request/response logging**
- ✅ **Celery task monitoring**
- ✅ **Database query logging** (in debug mode)

See [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment guide.
