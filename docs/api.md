# API reference

Interactive OpenAPI documentation is available at `/docs` when the server is running.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Service health |
| POST | `/api/traces` | Ingest a trace |
| GET | `/api/traces` | Search recent traces |
| GET | `/api/traces/{trace_id}` | Retrieve one trace |
| GET | `/api/metrics` | Aggregate observability metrics |
| POST | `/api/evaluations` | Run an evaluation dataset |
| GET | `/api/evaluations` | List evaluation runs |
| POST | `/api/prompts` | Create a prompt version |
| GET | `/api/prompts` | List prompt versions |
| POST | `/api/demo/seed` | Add deterministic demo records |
