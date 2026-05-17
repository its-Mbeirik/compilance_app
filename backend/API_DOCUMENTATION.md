# Compliance Verification API Documentation

## Overview

The Compliance Verification System provides REST API endpoints for uploading contracts and analyzing them against Mauritanian legal frameworks using a multi-agent LangGraph workflow.

## System Architecture

```
FastAPI Endpoints
    ↓
Contract Upload/Retrieval (contracts.py)
    ↓
Compliance Verification Orchestration (compliance.py)
    ↓
LangGraph Workflow (graph.py)
    ├→ Extraction Agent
    ├→ Legal Matching Agent
    ├→ Compliance Agent
    └→ Report Agent
    ↓
Vector Search / Legal Corpus (VectorStore)
    ↓
PostgreSQL + pgvector
```

## API Endpoints

### Contracts Management

#### POST /api/v1/contracts/upload
Upload a contract document for compliance verification.

**Request:**
```
Content-Type: multipart/form-data
- file: PDF or DOCX file
```

**Response:**
```json
{
  "contract_id": "uuid",
  "filename": "contract.pdf",
  "document_type": "contrat_travail",
  "status": "uploaded",
  "message": "Contract uploaded successfully..."
}
```

**Supported document types (auto-detected from filename):**
- `statuts_entreprise` - Company statutes (Articles of Incorporation)
- `contrat_travail` - Employment contracts

#### GET /api/v1/contracts
List all uploaded contracts with pagination.

**Query Parameters:**
- `skip`: Number of records to skip (default: 0)
- `limit`: Number of records to return (default: 10)

**Response:**
```json
{
  "contracts": [
    {
      "contract_id": "uuid",
      "filename": "statutes.docx",
      "document_type": "statuts_entreprise",
      "upload_date": "2026-05-17T10:30:00",
      "size_mb": 2.5,
      "status": "completed"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 10
}
```

#### GET /api/v1/contracts/{contract_id}
Retrieve metadata for a specific contract.

**Response:**
```json
{
  "contract_id": "uuid",
  "filename": "contract.pdf",
  "document_type": "contrat_travail",
  "upload_date": "2026-05-17T10:30:00",
  "size_mb": 1.2,
  "status": "completed"
}
```

### Compliance Verification

#### POST /api/v1/compliance/verify/{contract_id}
Trigger compliance verification for an uploaded contract.

**Workflow Steps:**
1. **Extraction Phase**: Parse contract text and extract clauses using DocumentProcessor
2. **Legal Matching Phase**: Match clauses against legal corpus using vector embeddings
3. **Compliance Checking Phase**: Detect violations, missing clauses, calculate score
4. **Report Generation Phase**: Create executive summary and recommendations

**Response:**
```json
{
  "contract_id": "uuid",
  "document_type": "contrat_travail",
  "analysis_date": "2026-05-17T10:35:00",
  "overall_status": "partially_compliant",
  "compliance_score": 78.5,
  "total_issues": 5,
  "critical_issues": 0,
  "high_issues": 2,
  "issues": [
    {
      "issue_id": "ISSUE_001",
      "severity": "high",
      "clause_reference": "Article 3",
      "issue_type": "weak_legal_reference",
      "description": "Clause may not align well with applicable law (similarity: 45%)",
      "legal_reference": "Code du Travail Article 25",
      "recommendation": "Review clause wording to improve alignment with legal requirements"
    }
  ],
  "summary": "⚠ This contrat_travail is partially compliant. Compliance score: 78.5%. Found 5 issues requiring attention.",
  "recommendations": [
    "Review and strengthen clause wording to align with legal requirements",
    "⚠️ Critical issues require immediate legal review and correction"
  ]
}
```

#### GET /api/v1/compliance/{contract_id}
Retrieve cached compliance report for a contract.

**Response:** Same format as verify endpoint.

#### POST /api/v1/compliance/{contract_id}/query
Interactive Q&A about compliance findings.

**Request:**
```json
{
  "question": "What are the missing clauses?"
}
```

**Response:**
```json
{
  "contract_id": "uuid",
  "question": "What are the missing clauses?",
  "answer": "Found 3 missing clauses: probation period clause, termination conditions clause..."
}
```

#### GET /api/v1/compliance/{contract_id}/export
Export compliance report in specified format.

**Query Parameters:**
- `format`: "json" (currently supported), "pdf", "docx" (planned)

**Response:**
```json
{
  "format": "json",
  "data": { /* full report object */ }
}
```

## Compliance Scoring Algorithm

The compliance score (0-100) is calculated using a weighted formula:

```
Compliance Score = 
  (clauses_with_matches / total_clauses) × 60 +
  (mandatory_coverage / 100) × 30 -
  min(issue_count × 2, 10)
```

**Components:**
- **Matching Score (60%)**: Percentage of clauses with matching legal articles
- **Mandatory Coverage (30%)**: Percentage of required clauses present
- **Issue Penalty (10%)**: Reduction based on number of detected issues

**Overall Status:**
- `compliant`: Score ≥ 90%
- `partially_compliant`: Score 70-89%
- `non_compliant`: Score < 70%

## Issue Types

| Type | Description | Typical Severity |
|------|-------------|------------------|
| `missing_legal_reference` | No matching legal articles found | High |
| `weak_legal_reference` | Low similarity to legal requirements | Medium |
| `missing_clause` | Mandatory clause not present | High |
| `non_compliant` | Clause contradicts legal requirements | Critical |

## Database Schema

### Contracts Table
```sql
CREATE TABLE contracts (
  id UUID PRIMARY KEY,
  filename VARCHAR(255),
  document_type VARCHAR(50),
  file_path VARCHAR(255),
  file_size_bytes INTEGER,
  status VARCHAR(50),
  error_message TEXT,
  uploaded_at TIMESTAMP,
  processed_at TIMESTAMP,
  created_at TIMESTAMP
);
```

### Compliance Reports Table
```sql
CREATE TABLE compliance_reports (
  id UUID PRIMARY KEY,
  contract_id UUID,
  overall_status VARCHAR(50),
  compliance_score FLOAT,
  total_issues INTEGER,
  critical_issues INTEGER,
  high_issues INTEGER,
  summary TEXT,
  extracted_clauses INTEGER,
  report_json JSONB,
  created_at TIMESTAMP
);
```

### Compliance Issues Table
```sql
CREATE TABLE compliance_issues (
  id UUID PRIMARY KEY,
  report_id UUID,
  severity VARCHAR(20),
  issue_type VARCHAR(100),
  clause_reference VARCHAR(255),
  description TEXT,
  legal_reference VARCHAR(255),
  recommendation TEXT,
  created_at TIMESTAMP
);
```

### Legal Documents Table
```sql
CREATE TABLE legal_documents (
  id UUID PRIMARY KEY,
  law_code VARCHAR(100),
  article VARCHAR(50),
  article_title VARCHAR(255),
  content TEXT,
  embedding Vector(1024),
  jurisdiction VARCHAR(50),
  category VARCHAR(100),
  effective_date TIMESTAMP,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
);
```

## Workflow Execution Flow

### 1. Extraction Agent
**Input:** Contract text
**Output:** Extracted clauses with metadata
```python
{
  "extracted_clauses": [
    {
      "id": "CLAUSE_001",
      "type": "Article",
      "title": "Constitution",
      "content": "...",
      "full_content": "...",
      "word_count": 150,
      "character_count": 800
    }
  ],
  "extraction_status": "success",
  "extraction_metadata": {
    "total_clauses": 25,
    "text_length": 15000
  }
}
```

### 2. Legal Matching Agent
**Input:** Extracted clauses
**Output:** Matched legal articles with similarity scores
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
          "relevance": "high"
        }
      ],
      "best_match_score": 0.87
    }
  ],
  "matching_status": "success",
  "matching_metadata": {
    "total_clauses_matched": 25,
    "clauses_with_matches": 24,
    "average_similarity": 0.75
  }
}
```

### 3. Compliance Agent
**Input:** Extracted clauses, legal matches
**Output:** Detected issues and compliance score
```python
{
  "compliance_issues": [
    {
      "id": "ISSUE_001",
      "clause_id": "CLAUSE_003",
      "severity": "high",
      "type": "missing_legal_reference",
      "description": "Clause has no matching legal articles",
      "recommendation": "Review this clause against current legislation"
    }
  ],
  "compliance_score": 78.5,
  "overall_status": "partially_compliant",
  "mandatory_clause_status": {
    "found": ["Article 1", "Article 2"],
    "missing": ["Article 7"],
    "coverage": 95.0
  },
  "issue_summary": {
    "total_issues": 5,
    "critical": 0,
    "high": 2,
    "medium": 2,
    "low": 1
  }
}
```

### 4. Report Agent
**Input:** All previous agent outputs
**Output:** Formatted report with recommendations
```python
{
  "final_report": {
    "metadata": {
      "generated_at": "2026-05-17T10:35:00Z",
      "contract_id": "uuid",
      "document_type": "contrat_travail"
    },
    "compliance": {
      "overall_status": "partially_compliant",
      "compliance_score": 78.5,
      "score_breakdown": {
        "critical_issues": 0,
        "high_issues": 2,
        "medium_issues": 2,
        "low_issues": 1
      }
    },
    "mandatory_clauses": { /* status object */ },
    "issues": [ /* issue list */ ],
    "summary": "...",
    "recommendations": [ /* recommendations */ ]
  }
}
```

## Error Handling

### Common Errors

| Status | Error | Solution |
|--------|-------|----------|
| 400 | No filename provided | Ensure file is attached in upload |
| 400 | Unsupported file type | Use PDF or DOCX only |
| 404 | Contract not found | Verify contract_id exists |
| 404 | Compliance report not found | Run verification first (POST /compliance/verify) |
| 500 | Extraction failed | Check file integrity and format |
| 500 | Workflow failed | Check database connection and legal corpus loaded |

## Testing

Run the end-to-end workflow test:

```bash
cd backend
python -m pytest tests/test_compliance_workflow.py -v

# Or run directly:
python tests/test_compliance_workflow.py
```

## Example Usage

### 1. Upload a Contract
```bash
curl -X POST "http://localhost:8000/api/v1/contracts/upload" \
  -F "file=@contracts/statutes.pdf"
```

### 2. Verify Compliance
```bash
curl -X POST "http://localhost:8000/api/v1/compliance/verify/{contract_id}"
```

### 3. Get Report
```bash
curl -X GET "http://localhost:8000/api/v1/compliance/{contract_id}"
```

### 4. Query About Findings
```bash
curl -X POST "http://localhost:8000/api/v1/compliance/{contract_id}/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What are the missing clauses?"}'
```

## Performance Considerations

- **Vector Search**: Optimized with IVFFlat indexes on pgvector embeddings
- **Batch Processing**: Database commits batched every 20 documents during corpus loading
- **Caching**: Compliance reports cached in database to avoid re-analysis
- **Extraction Time**: Typically 1-3 seconds depending on document length
- **Matching Time**: 5-15 seconds for vector similarity search against corpus
- **Total Workflow**: 15-40 seconds end-to-end per contract

## Legal Corpus

The system is pre-loaded with Mauritanian legal documents:
- Code du Travail (Labor Code)
- Code des Sociétés (Corporate Code)
- Code du Commerce (Commercial Code)
- Code des Obligations et des Contrats (Obligations Code)
- Convention Collective (Collective Bargaining Agreement)

## Architecture Notes

- **LangGraph**: Orchestrates agent workflow with state machine pattern
- **pgvector**: Enables semantic search on legal corpus embeddings
- **Sentence Transformers**: Generates 1024-dimensional embeddings for clauses and articles
- **SQLAlchemy ORM**: Type-safe database access with automatic migrations
- **FastAPI**: Async request handling with automatic OpenAPI documentation

