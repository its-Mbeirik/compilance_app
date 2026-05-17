# System Architecture

## Overview

The Compliance Verification System uses a multi-agent agentic architecture orchestrated with LangGraph, enabling specialized AI agents to work collaboratively on different aspects of contract compliance verification.

```
┌─────────────────────────────────────────────────────────────────┐
│                      User Interface (React)                      │
│                  (Next.js Frontend - Port 3000)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    HTTP REST API
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    FastAPI Backend                              │
│                   (Port 8000)                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────┐  │
│  │          LangGraph Multi-Agent Orchestration             │  │
│  │                                                          │  │
│  │  ┌──────────────┐      ┌──────────────┐               │  │
│  │  │ Extraction   │─────▶│ Legal        │               │  │
│  │  │ Agent        │      │ Matching     │               │  │
│  │  └──────────────┘      │ Agent        │               │  │
│  │                        └──────┬───────┘               │  │
│  │                               │                       │  │
│  │  ┌──────────────┐             │                       │  │
│  │  │ Compliance   │◀────────────┤                       │  │
│  │  │ Verification │             │                       │  │
│  │  │ Agent        │             │                       │  │
│  │  └──────┬───────┘             │                       │  │
│  │         │                     │                       │  │
│  │         └──────────────┬──────┘                       │  │
│  │                        │                             │  │
│  │  ┌──────────────┐      │                             │  │
│  │  │ Report       │◀─────┘                             │  │
│  │  │ Generation   │                                    │  │
│  │  │ Agent        │                                    │  │
│  │  └──────────────┘                                    │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                        │                                     │
├────────────┬───────────┼────────────┬──────────────────────┤
│            │           │            │                      │
▼            ▼           ▼            ▼                      ▼
Services:    Doc Parser Vector Store Database          LLM Provider
             (Unstructured (pgvector) (PostgreSQL)    (OpenAI/Claude)
              .io, spaCy)
```

## Agent Architecture

### 1. Extraction Agent

**Purpose:** Parse contracts and extract structured clause information.

**Responsibilities:**
- Load and parse PDF/DOCX documents
- Identify clause boundaries and structure
- Extract clause text with metadata (page, section, etc.)
- Use Named Entity Recognition (NER) for legal entities
- Return structured clause list

**Input:**
```
Raw contract document (text)
```

**Output:**
```python
{
    "clauses": [
        {
            "id": "CLAUSE_001",
            "type": "Article",
            "title": "Object and Scope",
            "content": "...",
            "location": "Page 1, Section 1",
            "confidence": 0.95
        },
        ...
    ]
}
```

**Technologies:**
- Unstructured.io / LangChain Document Loaders
- spaCy for NER
- LLM for semantic clause identification

### 2. Legal Matching Agent

**Purpose:** Match extracted clauses against applicable laws and regulations.

**Responsibilities:**
- Embed extracted clauses using sentence-transformers
- Perform semantic search against legal corpus in pgvector
- Score similarity of clause to legal articles
- Identify applicable laws for document type
- Return clause-to-law mappings

**Input:**
```
Extracted clauses + document type (statuts_entreprise or contrat_travail)
```

**Output:**
```python
{
    "matches": [
        {
            "clause_id": "CLAUSE_001",
            "matched_laws": [
                {
                    "law_code": "Code des Sociétés",
                    "article": "Article 5",
                    "relevance_score": 0.92
                }
            ]
        },
        ...
    ]
}
```

**Technologies:**
- sentence-transformers (multilingual-e5)
- pgvector for semantic search
- OpenAI embeddings (alternative)

### 3. Compliance Verification Agent

**Purpose:** Detect violations and compliance issues.

**Responsibilities:**
- Compare clauses against legal requirements
- Identify missing mandatory clauses for document type
- Detect contradictory or ambiguous clauses
- Analyze clause compliance with cited legal articles
- Calculate compliance score
- Categorize issues by severity (critical, high, medium, low, info)

**Input:**
```
Extracted clauses + legal matches + document type
```

**Output:**
```python
{
    "compliance_score": 85.5,
    "total_issues": 5,
    "critical_issues": 1,
    "high_issues": 2,
    "issues": [
        {
            "issue_id": "ISSUE_001",
            "severity": "critical",
            "clause_ref": "CLAUSE_003",
            "issue_type": "missing_clause",
            "description": "Mandatory probation period clause not found",
            "legal_ref": "Code du Travail Article 25",
            "recommendation": "Add clause specifying probation period"
        },
        ...
    ]
}
```

**Technologies:**
- Rule-based compliance checking (mandatory clause lists)
- LLM for semantic violation detection
- Custom scoring logic

### 4. Report Generation Agent

**Purpose:** Format findings into user-friendly compliance reports.

**Responsibilities:**
- Structure compliance analysis into report format
- Generate natural language summaries
- Create detailed recommendations
- Format for multiple export formats (PDF, DOCX, JSON)
- Organize issues by severity and type
- Add legal citations and references

**Input:**
```
Compliance analysis + contract metadata
```

**Output:**
```python
{
    "contract_id": "CONTRACT_001",
    "document_type": "contrat_travail",
    "analysis_date": "2026-05-16",
    "overall_status": "partially_compliant",
    "compliance_score": 85.5,
    "summary": "The contract contains mandatory labor clauses but lacks...",
    "recommendations": [
        "Add probation period clause",
        "Clarify salary deduction terms",
        ...
    ],
    "report_html": "<html>...</html>",
    "report_pdf": "base64_encoded_pdf"
}
```

**Technologies:**
- Jinja2 templates for report formatting
- python-docx for DOCX generation
- reportlab or similar for PDF
- LLM for natural language summaries

## Data Flow

### Complete Workflow

```
1. User uploads contract (PDF/DOCX)
   ↓
2. File stored temporarily
   ↓
3. Document Processing
   - Convert DOCX to text if needed
   - Parse PDF text
   ↓
4. Extraction Agent
   - Parse document structure
   - Extract clauses with metadata
   - Apply NER
   ↓
5. Legal Matching Agent
   - Embed clauses (1024-dim vectors)
   - Search pgvector for similar laws
   - Score and rank matches
   ↓
6. Compliance Verification Agent
   - Compare clauses to legal requirements
   - Detect missing/non-compliant clauses
   - Calculate compliance score
   - Identify violations by severity
   ↓
7. Report Generation Agent
   - Format findings
   - Generate recommendations
   - Create export-ready report
   ↓
8. Results Displayed to User
   - Summary dashboard
   - Issue details
   - Recommendations
   - Export options
```

## Database Schema (PostgreSQL + pgvector)

### Legal Documents Table
```sql
CREATE TABLE legal_documents (
    id SERIAL PRIMARY KEY,
    law_code VARCHAR(50),           -- "Code du Travail"
    article VARCHAR(50),             -- "Article 25"
    article_title VARCHAR(255),
    content TEXT,                    -- Full article text
    embedding vector(1024),          -- pgvector
    jurisdiction VARCHAR(50),        -- "Mauritanie"
    effective_date DATE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_law_code ON legal_documents(law_code);
CREATE INDEX idx_law_embedding ON legal_documents USING ivfflat (embedding vector_cosine_ops);
```

### Contracts Table
```sql
CREATE TABLE contracts (
    id UUID PRIMARY KEY,
    filename VARCHAR(255),
    document_type VARCHAR(50),       -- "statuts_entreprise" or "contrat_travail"
    file_path VARCHAR(255),
    status VARCHAR(20),              -- "uploaded", "processing", "completed", "failed"
    uploaded_at TIMESTAMP DEFAULT NOW(),
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Compliance Reports Table
```sql
CREATE TABLE compliance_reports (
    id UUID PRIMARY KEY,
    contract_id UUID REFERENCES contracts(id),
    overall_status VARCHAR(50),      -- "compliant", "non_compliant", "partially_compliant"
    compliance_score FLOAT,
    total_issues INT,
    critical_issues INT,
    high_issues INT,
    report_json JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### Issues Table
```sql
CREATE TABLE compliance_issues (
    id UUID PRIMARY KEY,
    report_id UUID REFERENCES compliance_reports(id),
    severity VARCHAR(20),            -- "critical", "high", "medium", "low", "info"
    issue_type VARCHAR(50),          -- "missing_clause", "non_compliant", etc.
    clause_reference VARCHAR(100),
    description TEXT,
    legal_reference VARCHAR(255),
    recommendation TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## LangGraph State Machine

```python
class ComplianceState(TypedDict):
    # Input
    contract_id: str
    contract_text: str
    document_type: str
    
    # Extraction phase
    extracted_clauses: Optional[List[dict]]
    extraction_errors: Optional[List[str]]
    
    # Legal matching phase
    legal_matches: Optional[List[dict]]
    matching_errors: Optional[List[str]]
    
    # Verification phase
    compliance_issues: Optional[List[dict]]
    compliance_score: Optional[float]
    verification_errors: Optional[List[str]]
    
    # Report phase
    final_report: Optional[dict]
```

**Graph Flow:**
```
State: contract_text, document_type
  ↓
[extract_node] → extraction_errors, extracted_clauses
  ↓
[legal_match_node] → matching_errors, legal_matches
  ↓
[verify_compliance_node] → verification_errors, compliance_issues, compliance_score
  ↓
[generate_report_node] → final_report
  ↓
END
```

## Vector Search Strategy

### Embedding Process

1. **Legal Corpus Preparation**
   - Load all laws (Code du Travail, Code des Sociétés, etc.)
   - Split into chunk: articles, sections
   - Clean and normalize text

2. **Embedding**
   - Use multilingual-e5 model
   - Creates 1024-dimensional vectors
   - Stored in pgvector

3. **Indexing**
   - Create IVFFlat index for fast retrieval
   - Optimized for cosine similarity

### Query Process

1. **Clause Embedding**
   - Extract clause text
   - Embed with same model as corpus
   - Maintains semantic consistency

2. **Similarity Search**
   ```sql
   SELECT law_code, article, content,
          1 - (embedding <=> query_embedding) as similarity
   FROM legal_documents
   WHERE law_code = ANY($1)  -- Filter by applicable laws
   ORDER BY embedding <=> query_embedding
   LIMIT 10;
   ```

3. **Ranking**
   - Score clauses by similarity
   - Apply document-type filters
   - Rank by relevance

## Integration Points

### Frontend-Backend Communication
- REST API (FastAPI)
- JSON request/response format
- WebSocket (optional for streaming results)

### Backend-LLM Integration
- OpenAI API (primary)
- LangChain/LangGraph for orchestration
- Prompt caching for optimization

### Backend-Database Integration
- SQLAlchemy ORM
- psycopg2 driver
- Connection pooling

### Backend-Document Processing
- Unstructured.io for PDF/DOCX
- spaCy for NLP/NER
- Custom text extraction

## Error Handling

Each agent implements:
- Input validation
- Error logging
- Graceful degradation
- Fallback mechanisms
- Status reporting

## Performance Considerations

1. **Caching**
   - Cache legal corpus in memory
   - Cache embeddings
   - Cache frequent queries

2. **Async Processing**
   - Document parsing: async
   - LLM calls: async with retry
   - Database operations: connection pooling

3. **Scalability**
   - Vector index optimization (IVFFlat)
   - Database query optimization
   - Batch processing support

## Security

- Input validation at API layer
- SQL injection prevention (SQLAlchemy parameterization)
- API authentication (JWT - to implement)
- Rate limiting (to implement)
- Secure file upload handling
- Sensitive data masking in logs
