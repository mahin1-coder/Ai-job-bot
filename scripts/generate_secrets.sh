#!/bin/bash
# Generate secure secrets for production deployment

echo "🔐 Generating Production Secrets..."
echo ""

SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)
POSTGRES_PASSWORD=$(openssl rand -hex 16)
REDIS_PASSWORD=$(openssl rand -hex 16)

echo "Add these to your .env.production file:"
echo ""
echo "SECRET_KEY=$SECRET_KEY"
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo "POSTGRES_PASSWORD=$POSTGRES_PASSWORD"
echo "REDIS_PASSWORD=$REDIS_PASSWORD"
echo ""
echo "⚠️  IMPORTANT: Store these securely! Never commit to git."
