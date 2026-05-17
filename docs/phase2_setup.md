# Phase 2: Core Implementation Setup

This guide covers setting up the database, loading the legal corpus, and implementing the agents.

## Prerequisites

- Docker & Docker Compose running
- PostgreSQL + pgvector container up and healthy
- Legal corpus file ready: `ressourse/les lois.txt`

## Step 1: Update Backend Dependencies

The requirements have been updated with new packages. Reinstall in the container:

```bash
# If running locally:
cd backend
pip install -r requirements.txt

# Or rebuild the Docker image:
docker-compose down
docker-compose up -d --build
```

## Step 2: Load Legal Corpus into Vector Database

### Option A: Docker Container

```bash
# SSH into the backend container
docker-compose exec backend bash

# Install dependencies if needed
pip install -r requirements.txt

# Run the corpus loader
python scripts/load_corpus.py
```

Expected output:
```
============================================================
Legal Corpus Loader
============================================================
Connecting to database...
Initializing database...
Parsing laws from: ...les lois.txt
Extracted 200+ articles
Embedding and loading articles...
  Processed 10/200 articles...
  Processed 20/200 articles...
  ...
✓ Successfully loaded 200 legal articles
✓ Corpus loading completed successfully!
```

### Option B: Local Python (if running backend locally)

```bash
cd backend

# Ensure database is accessible
export DATABASE_URL="postgresql://compliance_user:compliance_password@localhost:5432/compliance_db"
export OPENAI_API_KEY="your_key_here"

# Run loader
python scripts/load_corpus.py
```

## Step 3: Verify Database Setup

Connect to PostgreSQL to verify schema and data:

```bash
# Inside container or local
psql -h localhost -U compliance_user -d compliance_db

# Check tables
\dt

# Check legal documents count
SELECT law_code, COUNT(*) FROM legal_documents GROUP BY law_code;

# Test vector search
SELECT article, law_code, 1 - (embedding <=> '[...]'::vector) as similarity 
FROM legal_documents 
ORDER BY embedding <=> '[...]'::vector 
LIMIT 5;
```

## Step 4: Test API Health Check

```bash
# Health check (should show database connection status)
curl http://localhost:8000/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "compliance-verification-system"
}
```

## What's Implemented in Phase 2

### Database Models
- `LegalDocument` — Legal articles with vector embeddings
- `Contract` — Uploaded contracts with processing status
- `ComplianceReport` — Analysis results
- `ComplianceIssue` — Individual findings

### Services

#### VectorStore (`app/services/vector_store.py`)
```python
from app.services.vector_store import VectorStore
from sqlalchemy.orm import Session

# Usage in agents
vs = VectorStore(db_session)

# Find similar legal articles to a clause
matches = vs.find_similar_articles(
    clause_content="...",
    document_type="contrat_travail",
    top_k=5
)

# Get mandatory clause requirements
mandatory = vs.get_mandatory_clauses("contrat_travail")

# Get corpus statistics
stats = vs.get_database_stats()
```

#### DocumentProcessor (`app/services/document_processor.py`)
```python
from app.services.document_processor import DocumentProcessor

# Extract text from document
text, metadata = DocumentProcessor.process_document("contract.docx")

# Extract clauses
clauses = DocumentProcessor.extract_clauses(text)

# Normalize text
clean_text = DocumentProcessor.normalize_text(raw_text)
```

### Scripts

#### load_corpus.py
Loads legal corpus from `ressourse/les lois.txt` into pgvector with sentence-transformer embeddings.

## Phase 2 Checklist

- [ ] PostgreSQL + pgvector running
- [ ] Backend container built with new requirements
- [ ] Corpus loader executed successfully
- [ ] Legal documents visible in database
- [ ] API health check returns 200 OK
- [ ] Database stats show loaded articles
- [ ] VectorStore semantic search working

## Testing Vector Search

Create a test script to verify semantic search:

```python
# test_vector_search.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.services.vector_store import VectorStore

engine = create_engine("postgresql://compliance_user:compliance_password@localhost:5432/compliance_db")
Session = sessionmaker(bind=engine)
db = Session()

vs = VectorStore(db)

# Test 1: Semantic search
results = vs.semantic_search(
    query="What are the requirements for probation period?",
    law_codes=["Code du Travail", "Convention Collective du Travail"],
    top_k=3
)

print("Search Results:")
for doc, similarity in results:
    print(f"  {doc.article} ({doc.law_code}): {similarity:.2%}")
    print(f"    {doc.content[:100]}...")

# Test 2: Mandatory clauses
mandatory = vs.get_mandatory_clauses("contrat_travail")
print(f"\nMandatory Labor Contract Clauses:")
for clause in mandatory:
    print(f"  - {clause}")

# Test 3: Database stats
stats = vs.get_database_stats()
print(f"\nDatabase Statistics:")
print(f"  Total documents: {stats['total_documents']}")
for law_code, count in stats['by_law_code'].items():
    print(f"  {law_code}: {count}")
```

Run it:
```bash
cd backend
python test_vector_search.py
```

## Troubleshooting

### pgvector extension not found
```bash
# In container
psql -h db -U compliance_user -d compliance_db
CREATE EXTENSION vector;
\dx  # Verify extension installed
```

### Embedding model download takes too long
The first run of `load_corpus.py` downloads the embedding model (~500 MB). This is normal.
- Model: `sentence-transformers/multilingual-e5-large-instruct`
- Cached in: `~/.cache/huggingface/hub/`

### Database connection timeout
- Ensure PostgreSQL container is healthy: `docker-compose ps`
- Check DATABASE_URL is correct
- Wait a few seconds after Docker startup before running loader

### API shows "unhealthy"
The health check might time out on first startup. Wait 30 seconds and try again.

## Next Steps (Phase 3)

Once Phase 2 is complete:

1. **Implement Extraction Agent**
   - Parse documents into clauses
   - Use NER for legal entity extraction
   - Handle multi-language content

2. **Implement Legal Matching Agent**
   - Use VectorStore.find_similar_articles()
   - Score relevance of clause-to-law matches
   - Handle article updates and superseded laws

3. **Implement Compliance Verification Agent**
   - Check mandatory clause presence
   - Detect violations using LLM + rules
   - Calculate compliance scores by category

4. **Implement Report Generation Agent**
   - Format findings into structured report
   - Generate natural language recommendations
   - Export to PDF/DOCX/JSON

5. **Wire agents into LangGraph**
   - Create state machine nodes
   - Define state transitions
   - Add error handling and retries

## Files Modified/Created in Phase 2

```
backend/
├── app/
│   ├── models/
│   │   └── database.py                    # [NEW] Database models
│   ├── services/
│   │   ├── vector_store.py               # [UPDATED] Vector search implementation
│   │   └── document_processor.py          # [UPDATED] Document extraction
│   └── main.py                            # [UPDATED] Database initialization
├── scripts/
│   └── load_corpus.py                     # [NEW] Corpus loader
└── requirements.txt                       # [UPDATED] Added PyPDF2

docs/
└── phase2_setup.md                        # [NEW] This file
```

## Resources

- **Legal Corpus Source:** `ressourse/les lois.txt` (Mauritanian labor law)
- **Embedding Model:** [sentence-transformers/multilingual-e5-large-instruct](https://huggingface.co/sentence-transformers/multilingual-e5-large-instruct)
- **Vector DB:** [pgvector documentation](https://github.com/pgvector/pgvector)
- **SQLAlchemy + pgvector:** https://python.langchain.com/docs/integrations/vectorstores/pgvector

---

**Status:** Phase 2 ✅ Database & Corpus Ready  
**Next:** Phase 3 - Agent Implementation
