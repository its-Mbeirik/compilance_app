# Compliance Verification System - Backend

FastAPI-based backend for contract compliance verification using multi-agent architecture with LangGraph.

## Setup

### Installation

1. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

4. **Run migrations (if applicable)**
   ```bash
   # TODO: Add database migrations
   ```

### Development Server

```bash
uvicorn app.main:app --reload
```

Server runs on `http://localhost:8000`

API documentation: `http://localhost:8000/docs` (Swagger UI)

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app creation
│   ├── core/
│   │   ├── config.py        # Settings from environment
│   │   └── security.py      # Security utilities
│   ├── api/
│   │   ├── routes/
│   │   │   ├── health.py    # Health check endpoints
│   │   │   ├── contracts.py # Contract upload/management
│   │   │   └── compliance.py# Compliance verification
│   │   └── schemas.py       # Pydantic models
│   ├── agents/
│   │   ├── graph.py         # LangGraph state machine
│   │   ├── extraction_agent.py       # Clause extraction
│   │   ├── legal_matching_agent.py   # Legal matching
│   │   ├── compliance_agent.py       # Compliance checking
│   │   └── report_agent.py           # Report generation
│   ├── services/
│   │   ├── document_processor.py     # PDF/DOCX parsing
│   │   ├── vector_store.py           # pgvector operations
│   │   └── compliance_checker.py     # Compliance logic
│   └── models/
│       └── database.py      # SQLAlchemy models
├── tests/
│   ├── test_agents.py
│   └── test_api.py
├── data/
│   ├── laws/                # Legal corpus
│   └── test_contracts/      # Test documents
├── requirements.txt
├── .env.example
└── README.md
```

## Configuration

Environment variables (see `.env.example`):

- `OPENAI_API_KEY` — OpenAI API key
- `OPENAI_MODEL` — Model name (default: gpt-4-turbo-preview)
- `DATABASE_URL` — PostgreSQL connection string
- `PGVECTOR_ENABLED` — Enable vector search
- `EMBEDDING_MODEL` — Embedding model for vectors
- `EMBEDDING_DIM` — Embedding dimension
- `APP_HOST`, `APP_PORT` — Server host/port
- `CORS_ORIGINS` — Allowed CORS origins
- `MAX_UPLOAD_SIZE_MB` — Max file upload size
- `LOG_LEVEL` — Logging level

## API Routes

### Health Check
```
GET /api/v1/health
GET /api/v1/health/ready
```

### Contracts
```
POST /api/v1/contracts/upload
GET /api/v1/contracts/{contract_id}
GET /api/v1/contracts
```

### Compliance
```
POST /api/v1/compliance/verify/{contract_id}
GET /api/v1/compliance/{contract_id}
POST /api/v1/compliance/{contract_id}/query
GET /api/v1/compliance/{contract_id}/export
```

## Multi-Agent Architecture

### Agents

1. **Extraction Agent**
   - Parses contract documents
   - Extracts clauses using NER
   - Returns structured clause list

2. **Legal Matching Agent**
   - Matches clauses against legal corpus
   - Uses semantic search (pgvector)
   - Scores clause-law relevance

3. **Compliance Agent**
   - Detects violations and anomalies
   - Identifies missing mandatory clauses
   - Generates compliance score

4. **Report Agent**
   - Formats findings into structured report
   - Generates recommendations
   - Prepares export formats (PDF, DOCX, JSON)

### Workflow

```
Document Upload
      ↓
Extract Clauses (NER, LLM)
      ↓
Match Against Legal Corpus (Vector Search)
      ↓
Verify Compliance (Rule-based + LLM)
      ↓
Generate Report (Format & Export)
```

## Database

### PostgreSQL + pgvector

For vector similarity search over legal corpus:

```sql
-- Create pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Example table for laws
CREATE TABLE legal_documents (
    id SERIAL PRIMARY KEY,
    law_code VARCHAR(50),
    article VARCHAR(50),
    content TEXT,
    embedding vector(1024),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for fast similarity search
CREATE INDEX ON legal_documents USING ivfflat (embedding vector_cosine_ops);
```

## Testing

### Run Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_api.py
```

### With Coverage
```bash
pytest --cov=app tests/
```

## Logging

Configure logging level via `LOG_LEVEL` env var:
- `DEBUG` — Detailed debugging info
- `INFO` — General information
- `WARNING` — Warning messages
- `ERROR` — Error messages

## Docker

Build image:
```bash
docker build -f ../Dockerfile.backend -t compliance-backend .
```

Run container:
```bash
docker run -p 8000:8000 \
  -e OPENAI_API_KEY=your_key \
  -e DATABASE_URL=postgresql://... \
  compliance-backend
```

## Common Issues

### Import Errors
Ensure you're in the project root and have activated the virtual environment.

### Database Connection
Check `DATABASE_URL` in `.env` and ensure PostgreSQL is running.

### LLM API Errors
Verify `OPENAI_API_KEY` is valid and has sufficient quota.

### File Upload Issues
- Check `MAX_UPLOAD_SIZE_MB` limit
- Ensure `UPLOAD_DIR` is writable
- Verify file format (PDF or DOCX)

## Performance Optimization

- Vector search uses IVFFlat index on pgvector
- LLM calls are cached where applicable
- Document parsing is async
- Report generation can be queued for large batches

## Next Steps

- [ ] Implement agent nodes in LangGraph
- [ ] Load legal corpus into pgvector
- [ ] Implement document processing
- [ ] Set up database models
- [ ] Add authentication/authorization
- [ ] Implement caching layer
- [ ] Add batch processing support
