# FCI — Failure Capture & Intelligence Platform

A lightweight platform that captures HTTP 500 failures from microservices, aggregates operational signals, displays failure analytics, and generates AI-assisted operational insights.

## Architecture

![HLD Architecture](images/hld.svg)

## Prerequisites to run the project

- Docker Desktop
- Python 3.12
- Node.js 20
- postgres

## Quick Start

```bash
cp .env.example .env
docker compose up --build
```

| Service   | URL                        |
| --------- | -------------------------- |
| Dashboard | http://localhost:3000      |
| FCI API   | http://localhost:8000/docs |
| service-a | http://localhost:8001/docs |
| service-b | http://localhost:8002/docs |
| service-c | http://localhost:8003/docs |

The failure simulator runs automatically and hits mock endpoints every 10 seconds. After ~30 seconds, open the dashboard to see captured failures.

## Project Structure

```
FCI/
├── backend/           # FastAPI platform API
├── frontend/          # React dashboard
├── mock-services/     # 3 simulated microservices
├── scripts/           # Failure simulator
└── docker-compose.yml
```

## API Overview

### Failure Capture

- `POST /api/v1/failures` — ingest a single failure event
- `POST /api/v1/failures/batch` — bulk ingest

### Incidents

- `GET /api/v1/incidents` — list with filters (service, category, search, date range)
- `GET /api/v1/incidents/{id}` — incident detail

### Analytics

- `GET /api/v1/analytics/overview` — KPIs
- `GET /api/v1/analytics/trends?interval=hour|day`
- `GET /api/v1/analytics/services`
- `GET /api/v1/analytics/categories`
- `GET /api/v1/analytics/heatmap`
- `GET /api/v1/analytics/correlation`

### AI Insights

- `POST /api/v1/insights/analyze` — trigger analysis
- `GET /api/v1/insights` — list reports
- `GET /api/v1/insights/{group_id}` — report detail

## AI Workflow

The platform uses a **hybrid rule-engine + LLM** pipeline:

1. **Planner** — clusters failures into incident groups by service, category, and time window
2. **Rule Engine** — applies deterministic operational patterns (DB burst, cascading failures, auth spikes)
3. **LLM Analyzer** — enriches findings when an API key is configured (OpenAI or Anthropic)

By default (`LLM_PROVIDER=mock`), the rule engine runs standalone — no API key required.

### Enable LLM enrichment

```env
LLM_PROVIDER=openai
LLM_API_KEY=sk-...
LLM_MODEL=gpt-4o-mini
```

Or for Anthropic:

```env
LLM_PROVIDER=anthropic
LLM_API_KEY=sk-ant-...
LLM_MODEL=claude-3-5-haiku-latest
```

## Design Decisions

- **Middleware ingestion** — mock services report 500s via a shared FastAPI exception handler with retry; simpler and more reliable than log parsing for MVP
- **PostgreSQL + JSONB** — supports rich request metadata and concurrent writes from multiple services
- **Rule engine first** — operational reasoning works without AI; LLM adds nuance when available
- **Synchronous analysis** — on-demand via dashboard button; avoids Celery/Redis complexity for MVP

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL=postgresql://fci:fci@localhost:5432/fci
alembic upgrade head
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Mock services

```bash
cd mock-services
pip install -r requirements.txt
FCI_INGEST_URL=http://localhost:8000/api/v1/failures uvicorn service-a.main:app --port 8001
```

## Future Extensions

- write unit & integration tests for the backend
- add rate limiting for the API
- add a Notification service, to send notifications to the users when a new incident is created
- Async background workers
- Message queue ingestion (Kafka/RabbitMQ)
- Prometheus metrics endpoint for insights of backend performance
- OpenTelemetry tracing
- Auth on FCI API
- Refine search add elasticsearch for faster search
- add a Caching layer for the LLM API for analysis results to reduce token usage
