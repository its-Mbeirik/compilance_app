#!/bin/bash

set -e

echo "======================================================================"
echo "🚀 LOADING COMPLETE LEGAL CORPUS (All PDFs + TXT)"
echo "======================================================================"

COMPOSE_DIR="/c/Users/bouda/Desktop/iscae/s6/pfe2026/New folder/assistanteconformite"

# Step 1: Navigate to project
echo -e "\n📂 Step 1: Navigating to project..."
cd "$COMPOSE_DIR"

# Step 2: Rebuild containers with updated requirements
echo -e "\n🏗️  Step 2: Rebuilding Docker containers..."
echo "   (This may take 2-3 minutes...)"
docker-compose down
docker-compose up -d --build

# Wait for services
echo -e "\n⏳ Step 3: Waiting for services to be healthy..."
sleep 15

# Check health
echo "   Checking container status..."
docker-compose ps

# Step 4: Run corpus loader
echo -e "\n📚 Step 4: Loading legal corpus from all files..."
echo "   (This may take 5-10 minutes depending on your internet)..."
docker-compose exec -T backend python scripts/load_all_corpus.py

# Step 5: Verify
echo -e "\n✓ Step 5: Verifying database..."
docker-compose exec -T db psql -U compliance_user -d compliance_db -c \
  "SELECT law_code, COUNT(*) as count FROM legal_documents GROUP BY law_code ORDER BY count DESC;"

echo -e "\n======================================================================"
echo "✅ CORPUS LOADING COMPLETE!"
echo "======================================================================"
echo -e "\n🎯 Next steps:"
echo "   1. Open http://localhost:3000 to test the ChatGPT UI"
echo "   2. Upload a test contract (PDF or DOCX)"
echo "   3. Ask questions about compliance"
echo "   4. Check backend logs: docker-compose logs backend"
echo -e "\n📖 Documentation:"
echo "   • Phase 3 agents: See docs/architecture.md"
echo "   • API endpoints: See backend/README.md"
echo "   • Frontend UI: See UI_REDESIGN_SUMMARY.md"

