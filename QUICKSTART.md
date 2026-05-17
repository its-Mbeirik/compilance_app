# Quick Start Guide - Phase 3 Complete Implementation

This guide walks through starting the complete compliance verification system with all four agents integrated.

## Prerequisites

✓ PostgreSQL 14+ with pgvector extension
✓ Python 3.9+
✓ Node.js 18+
✓ Legal corpus loaded in database (see Phase 2)

## Step 1: Backend Setup (5 minutes)

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Configure environment
cat > .env << 'EOF'
DATABASE_URL=postgresql://user:password@localhost:5432/pfe_compliance
CORS_ORIGINS=["http://localhost:3000"]
LOG_LEVEL=INFO
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=true
EOF

# Start the backend server
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Expected Output**:
```
INFO:     Started server process [1234]
INFO:     Waiting for application startup.
INFO:     Application startup complete [with uvicorn.run]
INFO:     Uvicorn running on http://0.0.0.0:8000

Logs should show:
- Database initialized
- pgvector extension enabled
- Legal corpus loaded with document counts by law code
```

## Step 2: Frontend Setup (3 minutes)

In a new terminal:

```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cat > .env.local << 'EOF'
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
EOF

# Start development server
npm run dev
```

**Expected Output**:
```
> next dev

  ▲ Next.js 14.x.x
  - Local:        http://localhost:3000
  - Environments: .env.local

✓ Ready in 2.5s
```

## Step 3: Test the System

### Option A: Via Frontend UI

1. Open http://localhost:3000 in your browser
2. You should see the ChatGPT-style interface
3. Click "Upload Contract" (or drag a contract file)
4. Select a test contract (PDF or DOCX)
5. Click "Verify Compliance"
6. Watch the workflow progress in real-time
7. See the full compliance report with issues and recommendations

### Option B: Via API Tests

```bash
cd backend

# Run the end-to-end workflow test
python tests/test_compliance_workflow.py
```

This will:
- Test both document types (statuts_entreprise, contrat_travail)
- Run the complete 4-agent workflow
- Display extracted clauses, matched articles, compliance score, and recommendations

### Option C: Via cURL

```bash
# Create a test contract file
cat > test_contract.txt << 'EOF'
Article 1: Constitution
The company is established as a Société Anonyme.

Article 2: Duration
The duration of the company is 99 years.

Article 3: Capital
The capital is fixed at 5,000,000 ouguiyas.
EOF

# Upload contract
curl -X POST http://localhost:8000/api/v1/contracts/upload \
  -F "file=@test_contract.txt" \
  -o contract_response.json

# Extract contract_id from response
CONTRACT_ID=$(jq -r '.contract_id' contract_response.json)
echo "Contract ID: $CONTRACT_ID"

# Verify compliance
curl -X POST http://localhost:8000/api/v1/compliance/verify/$CONTRACT_ID \
  -H "Content-Type: application/json" | jq '.'

# Get report
curl -X GET http://localhost:8000/api/v1/compliance/$CONTRACT_ID | jq '.'
```

## Understanding the Workflow Output

### Workflow Stages

The compliance verification happens in 4 stages:

```
1. Extraction (1-2 sec)
   └─ Parses contract, extracts 20-50 clauses

2. Legal Matching (5-10 sec)
   └─ Matches each clause to legal articles
   └─ Calculates similarity scores

3. Compliance Check (1-2 sec)
   └─ Detects issues, calculates compliance score
   └─ Identifies missing mandatory clauses

4. Report Generation (< 1 sec)
   └─ Creates formatted report with recommendations
```

### Sample Output

```json
{
  "contract_id": "550e8400-e29b-41d4-a716-446655440000",
  "document_type": "contrat_travail",
  "overall_status": "partially_compliant",
  "compliance_score": 78.5,
  "total_issues": 5,
  "critical_issues": 0,
  "high_issues": 2,
  "summary": "⚠ This contrat_travail is partially compliant. Compliance score: 78.5%. Found 5 issues requiring attention. Missing 1 mandatory clause.",
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
  "recommendations": [
    "Review and strengthen clause wording to align with legal requirements",
    "Add missing probation period clause to ensure legal compliance"
  ]
}
```

## Key Features

### Document Type Detection
Automatically detects from filename:
- `statut*` → statuts_entreprise (Company Statutes)
- `contrat*` → contrat_travail (Employment Contract)
- `travail*` → contrat_travail

### Compliance Scoring
- **Matching Quality** (60%): % of clauses with legal matches
- **Mandatory Clauses** (30%): % of required clauses present
- **Issue Penalty** (10%): Deduction for detected issues

### Issue Severity Levels
- 🔴 **Critical**: Serious violations requiring immediate attention
- 🟠 **High**: Important issues that should be addressed
- 🟡 **Medium**: Clauses needing clarification
- 🔵 **Low**: Minor inconsistencies
- ℹ️ **Info**: Informational notices

## Testing Both Document Types

### 1. Company Statutes (statuts_entreprise)

Create `statutes_test.txt`:
```
STATUTS DE LA SOCIETE EXEMPLE S.A.R.L

Article 1: Constitution
Establishment as a Société Anonyme.

Article 2: Siège Social
Head office in Nouakchott, Mauritanie.

Article 3: Objet Social
Commercial and industrial activities.

Article 4: Durée
Duration of 99 years from registration.

Article 5: Capital
Capital fixed at 5,000,000 ouguiyas.

Article 6: Actions
Shares are nominative and indivisible.

Article 7: Conseil d'Administration
Administered by 3-9 board members.
```

Upload and verify:
```bash
curl -X POST http://localhost:8000/api/v1/contracts/upload \
  -F "file=@statutes_test.txt" | jq '.contract_id' -r | \
  xargs -I {} curl -X POST http://localhost:8000/api/v1/compliance/verify/{}
```

### 2. Employment Contract (contrat_travail)

Create `contract_test.txt`:
```
CONTRAT DE TRAVAIL INDIVIDUEL

Article 1: Identité des Parties
Employeur: EXAMPLE CORPORATION S.A.R.L
Salarié: [Employee Name]

Article 2: Nature et Lieu
Position: [Job Title]
Location: Nouakchott

Article 3: Période d'Essai
Three (3) month trial period, renewable once.

Article 4: Durée du Contrat
Indefinite duration contract.

Article 5: Rémunération
Monthly salary: [Amount] ouguiyas.

Article 6: Horaires
40 hours per week, Monday-Friday.

Article 7: Congés
30 days paid leave per year.

Article 8: Avantages Sociaux
Social security coverage as per law.

Article 9: Obligations
Compliance with company rules.

Article 10: Résiliation
Termination per Code du Travail.

Article 11: Litiges
Jurisdiction in Nouakchott.
```

## Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Check dependencies
pip list | grep -E "fastapi|sqlalchemy|langgraph|pgvector"

# Check database connection
psql postgresql://user:password@localhost:5432/pfe_compliance -c "SELECT 1"
```

### Frontend won't connect to backend
```bash
# Check backend is running
curl http://localhost:8000/api/v1/health

# Check CORS is configured
# Should see "Access-Control-Allow-Origin" in headers
curl -I -H "Origin: http://localhost:3000" http://localhost:8000/api/v1/health

# Check .env.local has correct API URL
cat frontend/.env.local
```

### No legal corpus in database
```bash
# Check if documents loaded
cd backend
python -c "
from app.main import SessionLocal, get_db
from app.services.vector_store import VectorStore

db = SessionLocal()
vs = VectorStore(db)
stats = vs.get_database_stats()
print(f'Total documents: {stats[\"total_documents\"]}')
for law_code, count in stats['by_law_code'].items():
    print(f'  {law_code}: {count}')
"

# If empty, load the corpus
python scripts/load_all_corpus.py
```

### Workflow takes too long
- First run takes longer (model download)
- Subsequent runs should be 15-30 seconds
- Check database indexes created
- Verify pgvector IVFFlat index exists

## Next Steps

1. **Test with real contracts**: Upload PDF/DOCX files from your organization
2. **Customize document type detection**: Add more patterns in contracts.py
3. **Adjust compliance thresholds**: Modify scoring weights in compliance_agent.py
4. **Add export functionality**: Implement PDF/DOCX report export
5. **Deploy to production**: Use gunicorn, nginx, and cloud database

## Project Completion

Phase 3 is now complete with:

✅ Four specialized agents working in sequence
✅ LangGraph orchestration of agent workflow
✅ REST API endpoints for contracts and compliance
✅ Frontend UI integrated with backend
✅ Vector similarity search on legal corpus
✅ Comprehensive compliance reporting
✅ Issue detection and recommendations
✅ End-to-end testing suite

The system is ready for production deployment and can handle real compliance verification workflows.

