# 🤖 AI Job Bot

**Stop wasting hours customizing resumes and cover letters.**

AI Job Bot automatically tailors your resume and writes cover letters for every job you apply to—using GPT-4 and semantic job matching.

---

## ✨ What It Does

1. **Upload your resume** (PDF or Word)
2. **Search for jobs** from 100,000+ listings (Adzuna, RemoteOK)
3. **AI matches** your resume to the best-fit jobs
4. **Auto-generates** tailored resumes and cover letters for each application
5. **Track everything** in one dashboard

---

## 🎯 Features

- ✅ **Resume Parser** - Extracts your experience, skills, education using GPT-4
- ✅ **Smart Job Search** - Scrapes Adzuna, RemoteOK, and other job boards
- ✅ **AI Matching** - Semantic search finds jobs that actually fit your background
- ✅ **Tailored Resumes** - Rewrites your bullets to match job keywords (no hallucinations)
- ✅ **Cover Letters** - Generates personalized 3-paragraph letters in seconds
- ✅ **Application Tracker** - Kanban board to manage all your applications

---

## 🚀 Quick Start (5 minutes)

### Prerequisites

- Docker installed ([Get Docker](https://docs.docker.com/get-docker/))
- OpenAI API key ([Get one here](https://platform.openai.com/api-keys))

### 1. Clone the repo

```bash
git clone https://github.com/mahin1-coder/Ai-job-bot.git
cd Ai-job-bot
```

### 2. Set up environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:

```bash
OPENAI_API_KEY=sk-your-key-here
```

### 3. Run with Docker

```bash
docker-compose up --build
```

### 4. Open the app

- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

That's it! 🎉

---

## 📸 Screenshots

### Resume Upload & Parsing
Upload your resume and let AI extract your skills, experience, and education automatically.

### Job Search & Matching
Search thousands of jobs and get AI-powered match scores showing which jobs fit your background.

### Tailored Resume Generation
Generate customized resumes that mirror job description keywords—no hallucinations.

### Application Tracker
Track all your applications in one place with status updates and AI-generated documents.

---

## 🎬 Demo Mode

Want to try without signing up? We've got sample data ready:

1. Visit http://localhost:3000
2. Click **"Try Demo"** on the landing page
3. Explore with a sample resume and pre-loaded jobs

No OpenAI key needed for demo mode!

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React, Vite, Tailwind CSS |
| **Backend** | FastAPI (Python), async/await |
| **Database** | PostgreSQL (async SQLAlchemy) |
| **AI** | OpenAI GPT-4, text-embedding-3-small |
| **Jobs APIs** | Adzuna, RemoteOK |
| **Background Jobs** | Celery + Redis |
| **Deployment** | Docker, Vercel (frontend), Render (backend) |

---

## 💰 Pricing

### Free Tier
- **5 jobs per day**
- AI resume tailoring
- Cover letter generation
- Application tracking

### Pro - $9/month
- **Unlimited jobs**
- Priority job scraping
- Email alerts for new matches
- Resume templates library
- Export to Word/PDF

**Coming soon!** Sign up for early access.

---

## 🚢 Deployment

### Deploy Frontend to Vercel (1 click)

1. Fork this repo
2. Visit [Vercel](https://vercel.com/new)
3. Import your forked repo
4. Set root directory to `frontend`
5. Add environment variable: `VITE_API_BASE_URL` = your backend URL
6. Deploy!

### Deploy Backend to Render

1. Create new Web Service on [Render](https://render.com)
2. Connect your GitHub repo
3. Set:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables from `.env.example`
5. Add PostgreSQL database (Render provides this)
6. Deploy!

### Deploy Backend to Railway

1. Visit [Railway](https://railway.app)
2. Click "New Project" → "Deploy from GitHub"
3. Select your repo
4. Railway auto-detects Python
5. Add PostgreSQL and Redis from the Railway dashboard
6. Set environment variables
7. Deploy!

---

## 📚 Documentation

- **API Reference**: Visit `/docs` endpoint after running
- **Production Deployment**: See [DEPLOYMENT.md](DEPLOYMENT.md)
- **Technical Details**: See [README_OLD.md](README_OLD.md) for architecture

---

## 🤝 Contributing

We welcome contributions! Here's how:

1. Fork the repo
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push: `git push origin feature/amazing-feature`
5. Open a Pull Request

---

## 📄 License

MIT License - feel free to use this for your own job search!

---

## 🙋 FAQ

**Q: Do I need coding experience?**  
A: Nope! Just Docker and an OpenAI API key.

**Q: How much does OpenAI cost?**  
A: ~$0.02 per resume + cover letter pair. Super cheap.

**Q: Can I use my own resume template?**  
A: Yes! We preserve your formatting and just rewrite the content.

**Q: What job boards does it search?**  
A: Adzuna (aggregates 100k+ jobs), RemoteOK, and we're adding LinkedIn scraping soon.

**Q: Is my data private?**  
A: Yes. Everything runs on your infrastructure. We don't store your data.

---

## ⭐ Star Us!

If this saved you time, give us a star on GitHub! It helps others discover the project.

---

**Built with ❤️ by developers who are tired of copy-pasting resumes.**

[GitHub](https://github.com/mahin1-coder/Ai-job-bot) • [Issues](https://github.com/mahin1-coder/Ai-job-bot/issues) • [Discussions](https://github.com/mahin1-coder/Ai-job-bot/discussions)
