# Production Deployment Guide

## Pre-deployment Checklist

### 1. Environment Setup

Create `.env.production`:
```bash
cp .env.example .env.production
```

Update the following:
```bash
# Generate secure secrets
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

# Production config
ENVIRONMENT=production
DEBUG=false
DATABASE_URL=postgresql+asyncpg://jobbot:${POSTGRES_PASSWORD}@postgres:5432/jobbot_db
REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379

# Your actual API keys
OPENAI_API_KEY=sk-...
ADZUNA_APP_ID=...
ADZUNA_API_KEY=...

# Your domain
ALLOWED_ORIGINS=https://yourdomain.com
```

### 2. SSL Certificate Setup

**Option A: Let's Encrypt (Recommended)**
```bash
# Initial certificate generation
docker-compose -f docker-compose.production.yml run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/www/certbot \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email \
  -d yourdomain.com \
  -d www.yourdomain.com

# Update nginx.conf with your domain
sed -i 's/yourdomain.com/your-actual-domain.com/g' nginx/nginx.conf
```

**Option B: Cloudflare (Alternative)**
- Use Cloudflare's Free SSL/TLS
- Set SSL mode to "Full (strict)"
- Keep nginx on HTTP only (Cloudflare handles HTTPS)

### 3. Database Migrations

```bash
# Run migrations
docker-compose -f docker-compose.production.yml exec api alembic upgrade head

# Create first superuser
docker-compose -f docker-compose.production.yml exec api python -c "
from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.auth import hash_password
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='admin@yourdomain.com',
            hashed_password=hash_password('change-this-password'),
            full_name='Admin User',
            is_superuser=True
        )
        db.add(admin)
        await db.commit()

asyncio.run(create_admin())
"
```

### 4. Deploy

```bash
docker-compose -f docker-compose.production.yml up -d --build
```

### 5. Post-Deployment

**Health checks:**
```bash
curl https://yourdomain.com/health
curl https://yourdomain.com/api/v1/health
```

**Monitor logs:**
```bash
docker-compose -f docker-compose.production.yml logs -f api
docker-compose -f docker-compose.production.yml logs -f worker
```

**Database backup:**
```bash
docker-compose -f docker-compose.production.yml exec postgres \
  pg_dump -U jobbot jobbot_db > backup_$(date +%Y%m%d).sql
```

## Cloud Deployment

### AWS ECS

1. **Push images to ECR:**
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

docker build -t ai-job-bot-backend ./backend
docker tag ai-job-bot-backend:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-job-bot-backend:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/ai-job-bot-backend:latest
```

2. **Create RDS PostgreSQL instance** (db.t3.micro for testing)

3. **Create ElastiCache Redis** (cache.t3.micro)

4. **Create ECS Task Definitions** for:
   - API service
   - Worker service
   - Frontend service

5. **Configure ALB** with:
   - Target groups for API + Frontend
   - SSL certificate (ACM)
   - Health checks

6. **Set environment variables** in ECS task definitions

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-job-bot-backend ./backend
gcloud builds submit --tag gcr.io/PROJECT_ID/ai-job-bot-frontend ./frontend

# Deploy API
gcloud run deploy ai-job-bot-api \
  --image gcr.io/PROJECT_ID/ai-job-bot-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="DATABASE_URL=...,OPENAI_API_KEY=..." \
  --add-cloudsql-instances=PROJECT_ID:us-central1:jobbot-db

# Deploy frontend
gcloud run deploy ai-job-bot-frontend \
  --image gcr.io/PROJECT_ID/ai-job-bot-frontend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="VITE_API_BASE_URL=https://api-xxx.run.app"
```

### DigitalOcean App Platform

1. Connect GitHub repository
2. Detect services automatically
3. Set environment variables
4. Deploy with zero config

## Monitoring & Observability

### 1. Sentry (Error Tracking)

Already integrated. Add to `.env.production`:
```bash
SENTRY_DSN=https://...@sentry.io/...
```

### 2. Prometheus + Grafana

Add to `docker-compose.production.yml`:
```yaml
prometheus:
  image: prom/prometheus
  volumes:
    - ./prometheus.yml:/etc/prometheus/prometheus.yml
  ports:
    - "9090:9090"

grafana:
  image: grafana/grafana
  ports:
    - "3001:3000"
  environment:
    - GF_SECURITY_ADMIN_PASSWORD=admin
```

### 3. Log Aggregation (ELK Stack)

```bash
docker run -d -p 9200:9200 -p 9300:9300 \
  -e "discovery.type=single-node" \
  docker.elastic.co/elasticsearch/elasticsearch:8.11.0

docker run -d -p 5601:5601 \
  -e "ELASTICSEARCH_HOSTS=http://elasticsearch:9200" \
  docker.elastic.co/kibana/kibana:8.11.0
```

## Scaling

### Horizontal Scaling

**API replicas:**
```yaml
api:
  deploy:
    replicas: 3
    resources:
      limits:
        cpus: '1'
        memory: 2G
```

**Worker replicas:**
```yaml
worker:
  deploy:
    replicas: 5  # Scale based on job queue depth
```

### Database Connection Pooling

Update `app/database.py`:
```python
engine = create_async_engine(
    settings.DATABASE_URL,
    pool_size=20,
    max_overflow=40,
    pool_pre_ping=True,
)
```

### Redis Caching

For job search results (already configured in `job_scraper.py`):
- Cache TTL: 30 minutes
- Invalidate on new scrape

## Security Hardening

### 1. Firewall Rules

```bash
# Allow only 80 and 443
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 2. Rate Limiting

Already configured in `main.py` with slowapi:
- 200 requests/minute per IP (global)
- 10 uploads/minute per IP

### 3. API Keys Rotation

Schedule monthly rotation:
```bash
# Add to crontab
0 0 1 * * /path/to/rotate_keys.sh
```

### 4. Database Encryption at Rest

**AWS RDS:**
- Enable encryption when creating instance

**PostgreSQL direct:**
```sql
ALTER SYSTEM SET ssl = on;
```

## Backup Strategy

### Automated Daily Backups

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Database backup
docker-compose -f docker-compose.production.yml exec -T postgres \
  pg_dump -U jobbot jobbot_db | gzip > "$BACKUP_DIR/db_$DATE.sql.gz"

# Upload to S3
aws s3 cp "$BACKUP_DIR/db_$DATE.sql.gz" s3://jobbot-backups/

# Cleanup old backups (keep 30 days)
find $BACKUP_DIR -name "db_*.sql.gz" -mtime +30 -delete
```

Schedule:
```bash
0 2 * * * /path/to/backup.sh
```

## Performance Optimization

### 1. CDN for Static Assets

Cloudflare (free tier):
- Automatic caching
- Image optimization
- DDoS protection

### 2. Database Indexes

```sql
CREATE INDEX CONCURRENTLY idx_jobs_title_company ON jobs(title, company);
CREATE INDEX CONCURRENTLY idx_applications_user_status ON applications(user_id, status);
```

### 3. pgvector for Embeddings

```sql
CREATE EXTENSION vector;
ALTER TABLE resumes ADD COLUMN embedding vector(1536);
ALTER TABLE jobs ADD COLUMN embedding vector(1536);
CREATE INDEX ON resumes USING ivfflat (embedding vector_cosine_ops);
```

Then update matching to use native vector similarity:
```python
SELECT * FROM jobs ORDER BY embedding <=> $1 LIMIT 10;
```

## Cost Optimization

### AWS (estimated monthly)

- **t3.micro API** (1x): $7.50
- **t3.micro Worker** (1x): $7.50
- **db.t3.micro RDS**: $15
- **cache.t3.micro Redis**: $12
- **ALB**: $16
- **S3 storage**: $1
- **CloudWatch**: $5
- **Total**: ~$64/month

### DigitalOcean App Platform

- **Basic plan** (all services): $12/month
- **Managed DB**: $15/month
- **Total**: ~$27/month

### Self-hosted VPS

- **Hetzner CX31** (2 vCPU, 8GB RAM): €6.90/month
- **Total**: ~$7.50/month

## Troubleshooting

### API not responding

```bash
docker-compose -f docker-compose.production.yml logs api
docker-compose -f docker-compose.production.yml restart api
```

### Database connection issues

```bash
docker-compose -f docker-compose.production.yml exec postgres psql -U jobbot -d jobbot_db
\dt  # List tables
\q   # Quit
```

### Celery tasks not running

```bash
docker-compose -f docker-compose.production.yml logs worker
docker-compose -f docker-compose.production.yml exec worker celery -A app.tasks.celery_app inspect active
```

### SSL certificate renewal

```bash
docker-compose -f docker-compose.production.yml run --rm certbot renew
docker-compose -f docker-compose.production.yml restart nginx
```

## Support

- GitHub Issues: https://github.com/mahin1-coder/Ai-job-bot/issues
- Documentation: See README.md
