# 🎯 Quick Reference Card

## Essential Commands

### Development
```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop all services
docker-compose down
```

### Production
```bash
# Deploy
docker-compose -f docker-compose.production.yml up -d --build

# Database migrations
docker-compose exec api alembic upgrade head

# Create admin user
./scripts/init_db.sh

# View production logs
docker-compose -f docker-compose.production.yml logs -f api worker
```

### Testing
```bash
# Run all tests
./scripts/run_tests.sh

# Run specific test
cd backend && pytest tests/test_auth.py -v

# Check coverage
cd backend && pytest --cov=app --cov-report=html
```

### Database
```bash
# Create migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Apply migrations
docker-compose exec api alembic upgrade head

# Rollback migration
docker-compose exec api alembic downgrade -1

# Access PostgreSQL
docker-compose exec postgres psql -U jobbot -d jobbot_db
```

### Celery Tasks
```bash
# Monitor worker
docker-compose exec worker celery -A app.tasks.celery_app inspect active

# See scheduled tasks
docker-compose exec beat celery -A app.tasks.celery_app inspect scheduled

# Purge queue
docker-compose exec worker celery -A app.tasks.celery_app purge
```

### Security
```bash
# Generate secrets
./scripts/generate_secrets.sh

# Rotate JWT secret
# 1. Generate new secret
# 2. Update .env.production
# 3. Restart API
docker-compose -f docker-compose.production.yml restart api
```

---

## API Endpoints

### Authentication
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/auth/register` | POST | Create account |
| `/api/v1/auth/login` | POST | Get JWT tokens |
| `/api/v1/auth/refresh` | POST | Refresh token |
| `/api/v1/auth/me` | GET | Current user (protected) |

### Resumes
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/resumes/upload` | POST | Yes | Upload + parse resume |
| `/api/v1/resumes/` | GET | Yes | List user's resumes |
| `/api/v1/resumes/{id}` | GET | Yes | Get resume details |
| `/api/v1/resumes/{id}` | DELETE | Yes | Delete resume |

### Jobs
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/jobs/search` | GET | Yes | Search jobs (scrapes APIs) |
| `/api/v1/jobs/match/{resume_id}` | POST | Yes | AI match resume to jobs |
| `/api/v1/jobs/` | GET | Yes | List saved jobs |

### Applications
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/applications/` | POST | Yes | Create application |
| `/api/v1/applications/stats` | GET | Yes | Dashboard statistics |
| `/api/v1/applications/{id}` | GET | Yes | Get application |
| `/api/v1/applications/{id}/status` | PATCH | Yes | Update status |

### AI Generation
| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/ai/generate` | POST | Yes | Generate resume + cover letter |
| `/api/v1/ai/stream/resume/{id}` | GET | Yes | Stream resume (SSE) |
| `/api/v1/ai/stream/cover-letter/{id}` | GET | Yes | Stream cover letter (SSE) |

---

## Environment Variables

### Required
```bash
OPENAI_API_KEY=sk-...        # OpenAI API key
SECRET_KEY=...               # App secret (32+ chars)
JWT_SECRET_KEY=...           # JWT secret (32+ chars)
DATABASE_URL=postgresql+asyncpg://user:pass@host/db
REDIS_URL=redis://localhost:6379
```

### Optional (with defaults)
```bash
ENVIRONMENT=development       # development|staging|production
DEBUG=false                   # Enable debug logging
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ADZUNA_APP_ID=...            # Job scraping (optional)
ADZUNA_API_KEY=...
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

---

## File Structure

```
ai-job-bot/
├── backend/
│   ├── app/
│   │   ├── routers/          # API endpoints
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── resumes.py
│   │   │   ├── jobs.py
│   │   │   ├── applications.py
│   │   │   └── ai.py
│   │   ├── services/         # Business logic
│   │   │   ├── resume_parser.py
│   │   │   ├── job_scraper.py
│   │   │   ├── job_matcher.py
│   │   │   └── ai_generator.py
│   │   ├── models/           # SQLAlchemy models
│   │   │   ├── user.py       # NEW
│   │   │   ├── resume.py
│   │   │   ├── job.py
│   │   │   └── application.py
│   │   ├── tasks/            # Celery tasks NEW
│   │   │   └── celery_app.py
│   │   └── utils/
│   │       └── auth.py       # JWT helpers NEW
│   ├── alembic/              # Migrations NEW
│   │   └── versions/
│   │       ├── 001_init.py
│   │       └── 002_add_users.py
│   └── tests/                # pytest tests NEW
│       ├── conftest.py
│       └── test_auth.py
├── frontend/
│   └── src/
│       ├── components/
│       └── services/
├── scripts/                  # Helper scripts NEW
│   ├── init_db.sh
│   ├── run_tests.sh
│   └── generate_secrets.sh
├── nginx/                    # Reverse proxy NEW
│   └── nginx.conf
├── .github/workflows/        # CI/CD NEW
│   └── ci-cd.yml
├── docker-compose.yml
├── docker-compose.production.yml  # NEW
├── DEPLOYMENT.md             # NEW
└── PRODUCTION_SUMMARY.md     # NEW
```

---

## Troubleshooting

### Issue: "Could not validate credentials"
**Solution**: Check JWT token expiry, get new token from `/auth/login`

### Issue: Celery tasks not running
```bash
# Check worker status
docker-compose logs worker

# Restart worker
docker-compose restart worker
```

### Issue: Database migrations failed
```bash
# Check current version
docker-compose exec api alembic current

# Reset to specific version
docker-compose exec api alembic downgrade <revision>
docker-compose exec api alembic upgrade head
```

### Issue: Port already in use
```bash
# Find process
lsof -i :8000

# Kill process
kill -9 <PID>
```

### Issue: CORS errors in frontend
**Solution**: Add frontend URL to `ALLOWED_ORIGINS` in `.env`

---

## Performance Tips

1. **Database**: Add indexes for frequently queried fields
2. **Caching**: Use Redis for job search results (30-min TTL)
3. **Rate limiting**: Adjust limits in `main.py`
4. **Worker scaling**: Increase Celery worker concurrency
5. **Database pooling**: Tune `pool_size` in `database.py`

---

## Deployment Checklist

- [ ] Generate production secrets (`./scripts/generate_secrets.sh`)
- [ ] Create `.env.production` with all secrets
- [ ] Update `ALLOWED_ORIGINS` with production domain
- [ ] Set up SSL certificate (Let's Encrypt)
- [ ] Update `nginx.conf` with actual domain
- [ ] Run database migrations (`alembic upgrade head`)
- [ ] Create admin user (`./scripts/init_db.sh`)
- [ ] Test all endpoints with Postman/curl
- [ ] Set up monitoring (Sentry DSN)
- [ ] Configure backups (daily pg_dump)
- [ ] Set up CI/CD secrets in GitHub
- [ ] Test CI/CD pipeline (push to main)
- [ ] Load test with realistic traffic
- [ ] Monitor logs for first 24 hours

---

## Resources

- **API Docs**: http://localhost:8000/docs (development)
- **GitHub**: https://github.com/mahin1-coder/Ai-job-bot
- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Production Summary**: [PRODUCTION_SUMMARY.md](PRODUCTION_SUMMARY.md)

---

**Quick Help**: Run `./scripts/init_db.sh` to set up everything!
