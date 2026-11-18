# Resume project entry — TraceForge

**TraceForge | LLM Observability & Evaluation API**  
*Python, FastAPI, SQLAlchemy, SQLite/PostgreSQL, Pydantic, Pytest, Docker*

- Built a modular FastAPI service to ingest and retrieve LLM interaction traces, capturing model metadata, latency, token counts, status, and request-level context.
- Implemented observability endpoints for request volume, failure rate, average latency, token consumption, and configurable estimated-cost aggregation.
- Developed deterministic evaluation workflows for exact-match and normalized string-similarity scoring, persisting aggregate results and case-level outcomes; added versioned prompt-template records.

**Important scope note:** This release does not yet implement distributed workers, production-grade user authentication, provider SDK integrations, semantic embeddings, or a React dashboard. Add those claims to a resume only after implementing and testing them.
