# Eve - Production-Style End-to-End AI Assistant

Eve is a full-stack, production-style AI assistant built as a comprehensive reference architecture for modern AI engineering. It demonstrates conversational AI, document ingestion, vector similarity search (RAG), agentic workflow orchestration, persistent conversations, observability, automated testing, containerization, and Infrastructure as Code.

---

## Architecture & Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend API** | FastAPI (Python 3.11+) | Async REST API, OpenAPI docs, SSE streaming |
| **Agent Orchestration** | LangGraph | State machine managing classification, retrieval & generation |
| **LLM Provider** | Groq (Llama 3.3 70B) | Ultra-low latency chat completion and streaming |
| **Embeddings & Search** | Jina AI (v3 1024-dim) | High-quality retrieval embeddings for queries and passages |
| **Database & Vector Store** | PostgreSQL + pgvector | Persistent conversations, document metadata, and HNSW vector index |
| **Frontend** | Next.js 14, Tailwind CSS | Responsive chat UI, real-time streaming, and document management |
| **Containerization** | Docker, Docker Compose | Multi-container local development and production container builds |
| **Infrastructure as Code** | OpenTofu | Declarative AWS infrastructure (VPC, RDS PostgreSQL, ECS Fargate) |
| **Observability** | Sentry, Comet Opik, CloudWatch | Exception monitoring, LLM tracing/evaluation, and structured JSON logs |
| **Quality & DevOps** | Ruff, MyPy, Pytest, GitHub Actions | Linting, static typing, test automation, and CI/CD pipelines |

---

## Quickstart (Local Development)

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL with pgvector (or Docker for `docker-compose`)

### 2. Environment Setup
```bash
# Clone the repository and navigate into eve
cd eve

# Copy example environment variables
cp .env.example .env
```
Edit `.env` to provide your `GROQ_API_KEY` and `JINA_API_KEY`.
*(Note: Eve provides built-in deterministic mocks, so the test suite and local walkthrough run cleanly even without live keys!)*

### 3. Running with Docker Compose (Recommended)
```bash
docker-compose up --build
```
- Frontend: http://localhost:3000
- Backend API & Swagger Docs: http://localhost:8000/docs
- PostgreSQL: `localhost:5432`

---

## Running Locally Without Docker

### Backend
```bash
cd backend
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## Testing & Quality Assurance

### Run Unit & Integration Tests
```bash
cd backend
pytest tests -v --cov=app
```
Eve includes comprehensive tests covering text chunking, document parsing, embeddings, vector retrieval, LangGraph agent nodes, and FastAPI endpoints.

### Linting & Formatting with Ruff
```bash
ruff check backend
ruff format --check backend
```

### Static Type Checking with MyPy
```bash
mypy backend/app
```

---

## Cloud Deployment

### 1. Frontend to Vercel
1. Connect your GitHub repository to Vercel.
2. Set the root directory to `frontend`.
3. Configure environment variable: `NEXT_PUBLIC_API_URL=https://api.yourdomain.com`.

### 2. Backend & Database to AWS via OpenTofu
OpenTofu configurations are located in `infrastructure/opentofu/`:
```bash
cd infrastructure/opentofu
tofu init
tofu plan -var="db_password=YourSecurePassword123!"
tofu apply -var="db_password=YourSecurePassword123!"
```

---

## Observability & Evaluation
- **Sentry**: Tracks uncaught runtime exceptions across FastAPI endpoints and database transactions.
- **Comet Opik**: Records spans for agent nodes (`classify_request`, `retrieve_context`, `generate_response`), logging latency and token usage.
- **AWS CloudWatch**: Standardized single-line JSON log output configured for production log ingestion and metric alarms.
