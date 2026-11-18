# TraceForge

**An observability and evaluation workbench for LLM applications.**

TraceForge helps developers inspect model interactions, measure request behavior, evaluate generated outputs against expected results, and maintain prompt versions.

> Status: early-stage portfolio project. The current release implements trace storage and retrieval, aggregate metrics, two deterministic evaluation metrics, prompt version records and a demo dataset. Distributed workers, production authentication, provider SDK integrations and a full frontend are planned rather than currently implemented.

## Why it exists

LLM applications can fail in ways that ordinary application logs do not explain. TraceForge provides a small, inspectable foundation for capturing model interactions and evaluating output quality.

## Features

- Trace ingestion with correlation identifiers.
- Searchable request history and trace details.
- Latency, token, error-rate and estimated-cost aggregates.
- Exact-match and normalized string-similarity evaluation.
- Persisted evaluation runs with case-level results.
- Versioned prompt templates.
- Deterministic demo data; no paid model API required.
- OpenAPI documentation and containerized local setup.

## Architecture and beginner guide

See [docs/architecture.md](docs/architecture.md) for the architecture and [docs/learning-path.md](docs/learning-path.md) for step-by-step setup, a code walkthrough, API examples, testing instructions and interview-safe project explanations. No React knowledge is required.

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open `http://localhost:8000/docs`.

Seed sample traces:

```bash
curl -X POST http://localhost:8000/api/demo/seed
```

Read metrics:

```bash
curl http://localhost:8000/api/metrics
```

## Docker

```bash
docker compose up --build
```

## Tests

The API tests use an isolated in-memory SQLite database. The suite covers health, trace creation/retrieval, demo seeding, metrics, evaluation persistence and request validation.

```bash
pip install -e '.[dev]'
pytest
```

## Engineering notes and limitations

- Cost estimates use a deliberately simple illustrative rate formula, not a live provider price feed.
- `normalized_similarity` is lexical similarity, not embedding-based semantic similarity.
- Evaluation currently runs in the API process; a Redis/Celery worker system is a planned extension.
- Write endpoints require an API key when `ENVIRONMENT=production`; configure a unique `API_KEY` before enabling production mode. This simple shared-key check is not user authentication or multi-tenant authorization.
- No frontend is included in this initial backend-focused release.

## Roadmap

- Redis-backed task queue with bounded retries and idempotency.
- Provider adapters and token accounting from provider usage metadata.
- Embedding-based semantic evaluation.
- Multi-user authentication and workspace isolation.
- React dashboard with trace explorer and evaluation comparison.
- PostgreSQL migration and load/performance tests.

## License

MIT. See [LICENSE](LICENSE).
