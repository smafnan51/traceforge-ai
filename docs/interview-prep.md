# Interview preparation: TraceForge

Use these notes to prepare explanations in your own words. Do not memorize claims you cannot demonstrate.

## 30-second project introduction

"TraceForge is a Python API project I built to explore observability for AI-powered applications. It stores request traces, exposes endpoints to search them and calculate basic metrics, and provides a small evaluation workflow to compare generated text with expected answers. I used FastAPI, Pydantic, SQLAlchemy, SQLite and Pytest."

## Questions you should be able to answer

### 1. Why did you build this?

AI applications need more than a final answer. Developers may need to investigate slow requests, failed requests, token usage and output quality. This project is a small learning implementation of those ideas.

### 2. What happens when a trace is submitted?

FastAPI receives JSON, Pydantic validates it against `TraceCreate`, the route builds a `Trace` SQLAlchemy model, and the database session saves it. The API returns the stored record with its generated trace ID.

### 3. What is the difference between a schema and a model?

A Pydantic schema describes and validates data crossing the API boundary. A SQLAlchemy model describes how data is stored in a database table.

### 4. How is the error rate calculated?

The service counts traces with status `error`, divides by the total number of traces, and returns zero when there are no traces. It is a simple all-time aggregate, not a time-windowed monitoring metric.

### 5. How does evaluation work?

For every case, the evaluation module compares `actual` and `expected`. Exact match trims whitespace and ignores case. Normalized similarity uses Python's `SequenceMatcher` ratio. The service averages the case scores and saves the run and details.

### 6. Is normalized similarity the same as semantic similarity?

No. It compares character sequences. It does not understand meaning, use embeddings or call an AI model. That is an important limitation of this first release.

### 7. How do you test the API?

Pytest and FastAPI's TestClient send HTTP requests to the application. The API tests replace the database dependency with a temporary in-memory SQLite database, so tests do not rely on the developer's local database file.

### 8. Why use SQLAlchemy?

It provides an ORM: Python classes represent database tables and the session handles database operations. It also lets the project switch database URLs without rewriting route logic.

### 9. How is the API protected?

In production mode, write endpoints require an `X-API-Key` header. The application refuses to run write operations with the default placeholder key. This is a basic shared-secret check, not full user authentication, authorization or multi-tenant security.

### 10. What would you improve next?

A sensible next step is database migrations, stronger authentication, pagination and time-windowed metrics. Provider integrations, background workers and a dashboard are larger future features. Do not say they already exist.

## Live demo sequence

1. Start the server using the commands in [learning-path.md](learning-path.md).
2. Open `/docs` in the browser.
3. Call `POST /api/demo/seed`.
4. Call `GET /api/traces` and inspect one returned trace.
5. Call `GET /api/metrics` and explain each field.
6. Call `POST /api/evaluations` with two short cases and compare the scores.
7. Show the tests by running `python -m pytest`.

## A good answer when you do not know something

Say what you understand, identify what you have not implemented, and explain how you would investigate it. Do not invent an answer or claim experience with a technology you have not used.
