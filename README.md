# Système Agentique de Vérification de Conformité Contractuelle

An intelligent multi-agent system for automated contract compliance verification against Mauritanian laws and regulations.

**Institution:** ISCAE Mauritanie  
**Department:** MQI  
**Program:** Licence Professionnelle (DI/IG/RT)  
**Supervisor:** Dr. Mohamed Ould Djibril  
**Team:** 3 students

---

## Project Overview

This system automates the verification of contract compliance with applicable laws. It specializes in two document types:

1. **Company Statutes** (Statuts d'entreprise) — verified against Code des Sociétés
2. **Work Contracts** (Contrats de travail) — verified against Code du Travail and collective agreements

### Key Features

- 📄 Multi-format document support (PDF, DOCX)
- 🤖 Multi-agent agentic architecture (LangGraph)
- 🔍 Semantic search over legal corpus (pgvector)
- 📊 Detailed compliance reports with legal citations
- 💬 Interactive Q&A mode for compliance questions
- 📈 Compliance scoring and risk assessment

---

## Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11+)
- **Agents:** LangGraph + LangChain
- **LLM:** OpenAI GPT-4 (or Claude/Llama via API)
- **Database:** PostgreSQL + pgvector
- **Document Processing:** Unstructured.io, spaCy, transformers

### Frontend
- **Framework:** Next.js 14 (React 18)
- **Styling:** TailwindCSS
- **Language:** TypeScript

### Infrastructure
- **Containerization:** Docker + Docker Compose
- **CI/CD:** GitHub Actions

---

## Quick Start

### Prerequisites
- Docker & Docker Compose installed
- OpenAI API key (or alternative LLM)
- Git

### Setup

1. **Clone repository**
   ```bash
   cd assistanteconformite
   ```

2. **Create environment files**
   ```bash
   cp backend/.env.example backend/.env
   cp frontend/.env.local.example frontend/.env.local
   ```

3. **Configure API keys**
   ```bash
   # backend/.env
   OPENAI_API_KEY=your_key_here
   ```

4. **Start services with Docker Compose**
   ```bash
   docker-compose up -d
   ```

5. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### Local Development (without Docker)

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

---

## Project Structure

```
assistanteconformite/
├── backend/
│   ├── app/
│   │   ├── agents/           # LangGraph agents
│   │   ├── api/routes/       # API endpoints
│   │   ├── services/         # Business logic
│   │   ├── core/             # Config, security
│   │   └── main.py           # FastAPI app
│   ├── data/
│   │   ├── laws/             # Legal corpus
│   │   └── test_contracts/   # Test documents
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   ├── pages/            # Next.js pages
│   │   ├── hooks/            # Custom hooks
│   │   └── types/            # TypeScript types
│   └── package.json
├── docker-compose.yml
├── Dockerfile.backend
├── Dockerfile.frontend
└── docs/
    ├── architecture.md
    ├── setup.md
    └── api.md
```

---

## API Endpoints

### Health Check
- `GET /api/v1/health` — System health status
- `GET /api/v1/health/ready` — Readiness probe

### Contract Management
- `POST /api/v1/contracts/upload` — Upload contract for analysis
- `GET /api/v1/contracts/{contract_id}` — Get contract metadata
- `GET /api/v1/contracts` — List uploaded contracts

### Compliance Verification
- `POST /api/v1/compliance/verify/{contract_id}` — Trigger compliance analysis
- `GET /api/v1/compliance/{contract_id}` — Get compliance report
- `POST /api/v1/compliance/{contract_id}/query` — Interactive Q&A
- `GET /api/v1/compliance/{contract_id}/export` — Export report (PDF/DOCX/JSON)

---

## Compliance Test Cases

### Test 1: Company Statutes
- **Input:** Statuts d'une entreprise (sample or test)
- **Verification Against:** Code des Sociétés + applicable laws
- **Expected Output:** Detailed compliance report with:
  - Missing mandatory clauses
  - Non-compliant provisions
  - Legal citations and recommendations

### Test 2: Work Contracts
- **Input:** Contrats de travail (sample or test)
- **Verification Against:** Code du Travail + collective labor agreements
- **Expected Output:** Compliance analysis focusing on:
  - Mandatory labor law clauses
  - Wage and benefits compliance
  - Termination and dispute resolution clauses

---

## Development Workflow

1. **Feature branches**: `feature/feature-name`
2. **Bug fixes**: `bugfix/issue-description`
3. **Pull requests** reviewed before merge to main

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Code Quality
```bash
# Backend linting
flake8 app/

# Frontend linting
npm run lint
npm run lint:fix
```

---

## Documentation

- [Architecture Guide](docs/architecture.md) — System design and agent orchestration
- [Setup Guide](docs/setup.md) — Detailed installation instructions
- [API Documentation](docs/api.md) — Complete API reference

---

## Deployment

### Docker Production Build
```bash
docker-compose -f docker-compose.yml up -d
```

### Environment Variables
See `backend/.env.example` and `frontend/.env.local.example` for all configurable options.

---

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
docker-compose logs db

# Verify connection
psql -h localhost -U compliance_user -d compliance_db
```

### Backend Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Frontend Build Issues
```bash
cd frontend
rm -rf .next node_modules
npm install
npm run build
```

---

## Contributing

1. Create a feature branch
2. Implement changes with tests
3. Ensure code passes linting
4. Submit PR with description

---

## License

This project is part of the ISCAE Mauritanie PFE program.

---

## Support

For issues or questions:
- **Supervisor:** Dr. Mohamed Ould Djibril (mohamed.djibril@iscae.mr)
- **Department:** MQI, ISCAE Mauritanie

---

**Status:** In Development 🚀
