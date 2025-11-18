#!/bin/bash
# Deployment script for Credit Risk App

set -e  # Exit on error

echo "🚀 Starting deployment..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${1:-production}
echo -e "${BLUE}Environment: ${ENVIRONMENT}${NC}"

# Step 1: Pull latest code
echo -e "${BLUE}📥 Pulling latest code...${NC}"
git pull origin main

# Step 2: Install backend dependencies
echo -e "${BLUE}📦 Installing backend dependencies...${NC}"
pip install -r requirements.txt

# Step 3: Build frontend
echo -e "${BLUE}⚛️  Building frontend...${NC}"
cd frontend
npm install
npm run build
cd ..

# Step 4: Run tests
echo -e "${BLUE}🧪 Running tests...${NC}"
pytest tests/backend/ || {
    echo -e "${RED}❌ Tests failed!${NC}"
    exit 1
}

# Step 5: Backup current deployment
echo -e "${BLUE}💾 Creating backup...${NC}"
BACKUP_DIR="backups/$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r models "$BACKUP_DIR/" 2>/dev/null || echo "No models to backup"
cp -r logs "$BACKUP_DIR/" 2>/dev/null || echo "No logs to backup"

# Step 6: Restart services
echo -e "${BLUE}🔄 Restarting services...${NC}"
if [ "$ENVIRONMENT" = "docker" ]; then
    docker-compose down
    docker-compose up -d --build
elif [ "$ENVIRONMENT" = "systemd" ]; then
    sudo systemctl restart credit-risk-api
    sudo systemctl restart credit-risk-frontend
else
    # Manual restart
    echo "Please restart services manually"
fi

# Step 7: Health check
echo -e "${BLUE}🏥 Running health check...${NC}"
sleep 5
HEALTH_CHECK=$(curl -s http://localhost:8000/health | grep -o '"status":"ok"' || echo "")
if [ -n "$HEALTH_CHECK" ]; then
    echo -e "${GREEN}✅ Deployment successful!${NC}"
    echo -e "${GREEN}API is healthy and running${NC}"
else
    echo -e "${RED}❌ Health check failed!${NC}"
    echo "Rolling back..."
    # Rollback logic here
    exit 1
fi

# Step 8: Cleanup
echo -e "${BLUE}🧹 Cleaning up...${NC}"
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo "📊 Deployment Summary:"
echo "  - Environment: $ENVIRONMENT"
echo "  - Backend: http://localhost:8000"
echo "  - Frontend: http://localhost:5173"
echo "  - Health: http://localhost:8000/health"
echo "  - Docs: http://localhost:8000/docs"
