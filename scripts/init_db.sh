#!/bin/bash
# Database initialization script

set -e

echo "🚀 Initializing AI Job Bot Database..."

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL..."
until docker-compose exec -T postgres pg_isready -U jobbot -d jobbot_db > /dev/null 2>&1; do
  sleep 1
done
echo "✅ PostgreSQL is ready"

# Run Alembic migrations
echo "📊 Running database migrations..."
docker-compose exec -T api alembic upgrade head
echo "✅ Migrations complete"

# Create default admin user (optional)
read -p "Create admin user? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    read -p "Admin email: " ADMIN_EMAIL
    read -sp "Admin password: " ADMIN_PASSWORD
    echo
    
    docker-compose exec -T api python -c "
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from app.utils.auth import hash_password

async def create_admin():
    async with AsyncSessionLocal() as db:
        admin = User(
            email='$ADMIN_EMAIL',
            hashed_password=hash_password('$ADMIN_PASSWORD'),
            full_name='Admin User',
            is_superuser=True,
            is_active=True
        )
        db.add(admin)
        await db.commit()
        print('✅ Admin user created:', '$ADMIN_EMAIL')

asyncio.run(create_admin())
"
fi

echo "
✅ Database setup complete!

Next steps:
1. Visit http://localhost:3000
2. Register an account or login with admin credentials
3. Upload a resume
4. Search for jobs
"
