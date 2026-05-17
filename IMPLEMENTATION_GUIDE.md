# Phase 3: Multi-Agent Integration Implementation Guide

## Overview

This document describes the complete implementation of Phase 3, where the four compliance verification agents are integrated into a LangGraph state machine and exposed through FastAPI REST endpoints.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   React Frontend                             │
│  (ChatGPT-style UI with file upload and chat interface)     │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/JSON
┌──────────────────────▼──────────────────────────────────────┐
│                   FastAPI Backend                            │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Contracts   │  │ Compliance   │  │ Health Checks    │  │
│  │ Endpoints   │  │ Endpoints    │  │                  │  │
│  └──────┬──────┘  └──────┬───────┘  └──────────────────┘  │
│         │                 │                                  │
│         └────────┬────────┘                                  │
│                  │                                            │
│         ┌────────▼──────────┐                                │
│         │  LangGraph        │                                │
│         │  State Machine    │                                │
│         │  (graph.py)       │                                │
│         └────────┬──────────┘                                │
│                  │                                            │
│      ┌───────────┼───────────┬──────────────┐                │
│      │           │           │              │                │
│  ┌───▼──┐  ┌───▼──┐  ┌──────▼──┐  ┌──────▼───┐             │
│  │ Extr.│  │Legad │  │Complian.│  │Report    │             │
│  │Agent │→ │Match │→ │ Agent   │→ │Agent     │             │
│  │      │  │Agent │  │         │  │          │             │
│  └──────┘  └──────┘  └─────────┘  └──────────┘             │
│      │           │           │              │                │
│      └───────────┼───────────┼──────────────┘                │
│                  │                                            │
│         ┌────────▼──────────┐                                │
│         │  Vector Store     │                                │
│         │  & Services       │                                │
│         └────────┬──────────┘                                │
│                  │                                            │
└──────────────────┼──────────────────────────────────────────┘
                   │ SQL + Vector Search
┌──────────────────▼──────────────────────────────────────────┐
│        PostgreSQL + pgvector                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Legal Docs   │  │ Contracts    │  │ Compliance       │  │
│  │ (Embeddings) │  │ (Metadata)   │  │ Reports & Issues │  │
│  └──────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## File Structure

### Backend

```
backend/
├── app/
│   ├── agents/
│   │   ├── extraction_agent.py      # Parse contracts → extract clauses
│   │   ├── legal_matching_agent.py  # Match clauses → legal articles
│   │   ├── compliance_agent.py      # Detect violations → calculate score
│   │   ├── report_agent.py          # Format findings → recommendations
│   │   └── graph.py                 # LangGraph state machine orchestration
│   ├── api/
│   │   └── routes/
│   │       ├── contracts.py         # POST /contracts/upload, GET /contracts/{id}
│   │       ├── compliance.py        # POST /compliance/verify/{id}, GET reports
│   │       └── health.py            # GET /health endpoint
│   ├── models/
│   │   └── database.py              # SQLAlchemy ORM models
│   ├── services/
│   │   ├── vector_store.py          # Semantic search on embeddings
│   │   └── document_processor.py    # Extract text from PDF/DOCX
│   ├── core/
│   │   └── config.py                # Settings & configuration
│   └── main.py                      # FastAPI app factory
├── tests/
│   └── test_compliance_workflow.py   # E2E workflow test
├── API_DOCUMENTATION.md             # Complete API reference
└── requirements.txt
```

### Frontend

```
frontend/
├── lib/
│   └── api.ts                       # API client & types
├── hooks/
│   └── useCompliance.ts             # React hook for workflow
├── components/
│   ├── ComplianceReportCard.tsx     # Report display component
│   ├── ChatInterface.tsx            # Chat UI with file upload
│   └── ...other components
└── pages/
    └── index.tsx                    # Main chat page
```

## Component Details

### 1. Extraction Agent (`extraction_agent.py`)

**Purpose**: Parse contract text and extract clause-like sections

**Process**:
1. Normalize text (remove control characters, standardize whitespace)
2. Extract clauses using regex patterns (Article, Section, Clause)
3. Enrich each clause with metadata (word count, character count)

**Input State**:
```python
{
  "contract_text": str,      # Full contract document
  "document_type": str       # "statuts_entreprise" or "contrat_travail"
}
```

**Output State**:
```python
{
  "extracted_clauses": [
    {
      "id": "CLAUSE_001",
      "type": "Article",
      "title": "...",
      "content": "...",
      "full_content": "...",
      "word_count": int,
      "character_count": int
    }
  ],
  "extraction_status": "success" | "failed",
  "extraction_metadata": {
    "total_clauses": int,
    "text_length": int
  }
}
```

### 2. Legal Matching Agent (`legal_matching_agent.py`)

**Purpose**: Match extracted clauses against legal corpus using semantic search

**Process**:
1. For each clause, encode to embedding using SentenceTransformer
2. Search legal_documents table using pgvector similarity (L2 distance)
3. Return top-5 matching articles with similarity scores

**Input State**:
```python
{
  "extracted_clauses": List[Dict],
  "document_type": str
}
```

**Output State**:
```python
{
  "legal_matches": [
    {
      "clause_id": "CLAUSE_001",
      "clause_type": "Article",
      "matched_articles": [
        {
          "law_code": "Code du Travail",
          "article": "Article 25",
          "article_title": "Duration of Employment",
          "content_summary": "...",
          "similarity_score": 0.87,
          "relevance": "high" | "medium" | "low"
        }
      ],
      "best_match_score": 0.87
    }
  ],
  "matching_status": "success" | "failed",
  "matching_metadata": {
    "total_clauses_matched": int,
    "clauses_with_matches": int,
    "average_similarity": float
  }
}
```

### 3. Compliance Agent (`compliance_agent.py`)

**Purpose**: Detect compliance violations and calculate overall score

**Detections**:
1. **Missing Legal Reference**: No matching articles found (severity: HIGH)
2. **Weak Legal Reference**: Similarity < 0.5 (severity: MEDIUM)
3. **Missing Mandatory Clause**: Required clause not present (severity: HIGH)
4. **Non-Compliant**: Clause contradicts legal requirements (severity: CRITICAL)

**Scoring Formula**:
```
Score = (matches/total)*60 + (mandatory_coverage/100)*30 - min(issues*2, 10)
```

**Input State**:
```python
{
  "extracted_clauses": List[Dict],
  "legal_matches": List[Dict],
  "document_type": str,
  "matching_metadata": Dict
}
```

**Output State**:
```python
{
  "compliance_issues": [
    {
      "id": "ISSUE_001",
      "clause_id": "CLAUSE_001",
      "severity": "critical" | "high" | "medium" | "low",
      "type": "missing_legal_reference" | "weak_legal_reference" | ...,
      "description": str,
      "legal_reference": str,
      "recommendation": str
    }
  ],
  "compliance_score": float,  # 0-100
  "overall_status": "compliant" | "partially_compliant" | "non_compliant",
  "mandatory_clause_status": {
    "found": List[str],
    "missing": List[str],
    "coverage": float  # percentage
  },
  "issue_summary": {
    "total_issues": int,
    "critical": int,
    "high": int,
    "medium": int,
    "low": int
  }
}
```

### 4. Report Agent (`report_agent.py`)

**Purpose**: Format findings into executive report with recommendations

**Process**:
1. Generate executive summary based on status and score
2. Categorize issues by type and severity
3. Generate actionable recommendations

**Input State**: All previous outputs

**Output State**:
```python
{
  "final_report": {
    "metadata": {
      "generated_at": "ISO timestamp",
      "contract_id": str,
      "document_type": str
    },
    "compliance": {
      "overall_status": str,
      "compliance_score": float,
      "score_breakdown": {
        "critical_issues": int,
        "high_issues": int,
        "medium_issues": int,
        "low_issues": int
      }
    },
    "mandatory_clauses": Dict,
    "issues": List[Dict],
    "summary": str,
    "recommendations": List[str],
    "extraction_metadata": Dict,
    "matching_metadata": Dict
  },
  "report_status": "success" | "failed"
}
```

## API Integration

### Contract Upload Flow

```
POST /api/v1/contracts/upload
  │
  ├─ Validate file format (PDF/DOCX)
  ├─ Save to disk (uploads/{contract_id}/)
  ├─ Create Contract record (status="uploaded")
  └─ Return ContractUploadResponse
       {
         contract_id: uuid,
         filename: str,
         document_type: "statuts_entreprise"|"contrat_travail"
       }
```

### Compliance Verification Flow

```
POST /api/v1/compliance/verify/{contract_id}
  │
  ├─ Retrieve Contract from database
  ├─ Extract text from file (DocumentProcessor)
  ├─ Run LangGraph workflow:
  │   ├─ Extraction Agent
  │   ├─ Legal Matching Agent
  │   ├─ Compliance Agent
  │   └─ Report Agent
  ├─ Update Contract status = "completed"
  ├─ Save ComplianceReport to database
  ├─ Save ComplianceIssues to database
  └─ Return ComplianceReport
       {
         contract_id: str,
         overall_status: "compliant"|"partially_compliant"|"non_compliant",
         compliance_score: 78.5,
         total_issues: 5,
         issues: [...],
         recommendations: [...]
       }
```

## Running the System

### 1. Start the Backend

```bash
cd backend

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export DATABASE_URL="postgresql://user:password@localhost:5432/pfe_compliance"
export CORS_ORIGINS='["http://localhost:3000"]'

# Run database migrations
python -m alembic upgrade head  # If using alembic

# Start server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. Start the Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
export NEXT_PUBLIC_API_URL="http://localhost:8000/api/v1"

# Start dev server
npm run dev
```

### 3. Run End-to-End Tests

```bash
cd backend

# Test the workflow
python tests/test_compliance_workflow.py
```

## Example Usage

### 1. Upload a Contract

```bash
curl -X POST http://localhost:8000/api/v1/contracts/upload \
  -F "file=@statutes.pdf"
```

Response:
```json
{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "filename": "statutes.pdf",
  "document_type": "statuts_entreprise",
  "status": "uploaded",
  "message": "Contract uploaded successfully..."
}
```

### 2. Verify Compliance

```bash
curl -X POST http://localhost:8000/api/v1/compliance/verify/550e8400-e29b-41d4-a716-446655440000
```

Response:
```json
{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type": "statuts_entreprise",
  "overall_status": "partially_compliant",
  "compliance_score": 82.5,
  "total_issues": 3,
  "issues": [...],
  "summary": "⚠ This statuts_entreprise is partially compliant...",
  "recommendations": [...]
}
```

### 3. Query Findings

```bash
curl -X POST http://localhost:8000/api/v1/compliance/550e8400-e29b-41d4-a716-446655440000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the missing clauses?"}'
```

## Testing Checklist

- [ ] Backend starts without errors
- [ ] Database initializes with pgvector extension
- [ ] Legal corpus loads correctly (check logs for document count)
- [ ] File upload endpoint accepts PDF and DOCX
- [ ] Compliance verification triggers workflow
- [ ] All four agents execute sequentially
- [ ] Report saves to database correctly
- [ ] Frontend connects to backend API
- [ ] Chat interface displays compliance report
- [ ] Query feature works on compliance findings
- [ ] Test both document types (statuts_entreprise, contrat_travail)

## Performance Tuning

### Vector Search Optimization
- IVFFlat index on legal_documents.embedding
- Adjust ivfflat parameters in database.py
- Monitor query time with EXPLAIN ANALYZE

### Database Optimization
- Connection pooling (pre_ping=True in engine config)
- Index coverage for contracts, compliance_reports tables
- Batch commits for large corpus loads

### API Response Time
- Cache compiled LangGraph workflow
- Pre-load embeddings model on startup
- Consider implementing request queuing for long-running verifications

## Troubleshooting

### Issue: "Contract not found"
- Verify contract_id is correct UUID
- Check uploads directory exists
- Confirm Contract record created in database

### Issue: "No legal corpus loaded"
- Check if legal_documents table populated
- Run `scripts/load_all_corpus.py`
- Verify database connection and pgvector extension

### Issue: "Embedding model not found"
- Ensure SentenceTransformer downloaded
- Check `~/.cache/huggingface/` directory
- Manual download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/multilingual-MiniLM-L12-v2')"`

### Issue: CORS errors in frontend
- Check `CORS_ORIGINS` environment variable
- Add http://localhost:3000 to allowed origins
- Verify backend starts with proper CORS middleware

## Next Steps

1. **Report Export**: Implement PDF/DOCX export functionality
2. **Report Caching**: Add Redis for faster report retrieval
3. **Interactive Agent**: Add Q&A agent for deeper compliance questions
4. **Batch Processing**: Queue system for processing multiple contracts
5. **WebSocket**: Real-time workflow progress streaming
6. **Analytics**: Dashboard with compliance trends and statistics

