# Phase 2 - Quick Start Guide

## TL;DR - Get Running in 5 Minutes

### 1. Ensure Docker containers are healthy
```bash
cd C:\Users\bouda\Desktop\iscae\s6\pfe2026\New\ folder\assistanteconformite
docker-compose ps
# Should show: db (healthy), backend (healthy), frontend (healthy)
```

### 2. Load the legal corpus
```bash
# Option A: Docker
docker-compose exec backend python scripts/load_corpus.py

# Option B: Local Python (if you have dependencies installed)
cd backend
python scripts/load_corpus.py
```

### 3. Verify it worked
```bash
curl http://localhost:8000/api/v1/health
# Should return 200 OK with status
```

### 4. Check database
```bash
docker-compose exec db psql -U compliance_user -d compliance_db -c \
  "SELECT law_code, COUNT(*) FROM legal_documents GROUP BY law_code;"
```

## What Changed in Phase 2

### New Files
- `backend/app/models/database.py` - SQLAlchemy models with pgvector
- `backend/scripts/load_corpus.py` - Corpus loader script
- `docs/phase2_setup.md` - Detailed setup guide
- `PHASE2_QUICKSTART.md` - This file

### Updated Files
- `backend/app/services/vector_store.py` - Full semantic search implementation
- `backend/app/services/document_processor.py` - Document extraction (DOCX, PDF)
- `backend/app/main.py` - Database initialization on startup
- `backend/requirements.txt` - Added PyPDF2

## Architecture Ready

```
┌──────────────────────────────────────────────────┐
│         Legal Corpus (200+ articles)             │
│         PostgreSQL + pgvector                    │
│    (Mauritanian labor & corporate law)           │
└────────────────────────────┬─────────────────────┘
                             │
                      Vector Search
                             │
┌────────────────────────────▼─────────────────────┐
│         VectorStore Service                      │
│  - Semantic search on articles                   │
│  - Mandatory clause detection                    │
│  - Corpus statistics                             │
└────────────────────────────┬─────────────────────┘
                             │
                  Extraction & Matching
                             │
┌────────────────────────────▼─────────────────────┐
│    DocumentProcessor Service                     │
│  - Extract text from DOCX/PDF                    │
│  - Parse clauses                                 │
│  - Text normalization                            │
└──────────────────────────────────────────────────┘
```

## Next Steps: Phase 3

Implement the four agents:

1. **Extraction Agent** - Parse contracts into clauses
2. **Legal Matching Agent** - Match clauses to laws using VectorStore
3. **Compliance Agent** - Detect violations and missing clauses
4. **Report Agent** - Generate formatted reports

See `docs/architecture.md` for detailed agent workflows.

## Verify Everything Works

Test API endpoints:
```bash
# Health check
curl http://localhost:8000/api/v1/health

# Upload a test contract
curl -X POST -F "file=@test_contract.pdf" \
  http://localhost:8000/api/v1/contracts/upload

# Verify frontend
open http://localhost:3000
```

---

**Status:** ✅ Phase 2 Complete - Database & Corpus Loaded  
**Ready for:** Phase 3 - Agent Implementation
