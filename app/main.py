from contextlib import asynccontextmanager
from uuid import uuid4
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from sqlalchemy import desc, func, select
from sqlalchemy.orm import Session
from app.config import settings
from app.database import Base, engine, get_db
from app.evaluation import evaluate
from app.models import EvaluationRun, PromptVersion, Trace
from app.schemas import EvaluationRequest, PromptCreate, TraceCreate

@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield

app = FastAPI(title=settings.app_name, version="0.1.0", lifespan=lifespan,
              description="LLM observability and evaluation workbench")

def require_api_key(x_api_key: str | None = Header(default=None)):
    if settings.environment == "production" and x_api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.get("/health")
def health():
    return {"status": "ok", "service": "traceforge-api"}

@app.post("/api/traces", dependencies=[Depends(require_api_key)])
def create_trace(payload: TraceCreate, db: Session = Depends(get_db)):
    trace = Trace(trace_id=str(uuid4()), provider=payload.provider, model=payload.model,
        prompt=payload.prompt, response=payload.response, status=payload.status,
        latency_ms=payload.latency_ms, input_tokens=payload.input_tokens,
        output_tokens=payload.output_tokens,
        estimated_cost_usd=round(payload.input_tokens * 0.000001 + payload.output_tokens * 0.000002, 8),
        error_message=payload.error_message, metadata_json=payload.metadata)
    db.add(trace); db.commit(); db.refresh(trace)
    return serialize_trace(trace)

@app.get("/api/traces")
def list_traces(q: str | None = None, limit: int = Query(default=50, ge=1, le=200),
                db: Session = Depends(get_db)):
    statement = select(Trace).order_by(desc(Trace.created_at)).limit(limit)
    if q:
        statement = select(Trace).where(
            Trace.prompt.contains(q) | Trace.response.contains(q) | Trace.trace_id.contains(q)
        ).order_by(desc(Trace.created_at)).limit(limit)
    return [serialize_trace(row) for row in db.scalars(statement).all()]

@app.get("/api/traces/{trace_id}")
def get_trace(trace_id: str, db: Session = Depends(get_db)):
    trace = db.scalar(select(Trace).where(Trace.trace_id == trace_id))
    if not trace: raise HTTPException(status_code=404, detail="Trace not found")
    return serialize_trace(trace)

@app.get("/api/metrics")
def metrics(db: Session = Depends(get_db)):
    total = db.scalar(select(func.count(Trace.id))) or 0
    failures = db.scalar(select(func.count(Trace.id)).where(Trace.status != "success")) or 0
    latency = db.scalar(select(func.avg(Trace.latency_ms))) or 0
    tokens = db.scalar(select(func.sum(Trace.input_tokens + Trace.output_tokens))) or 0
    cost = db.scalar(select(func.sum(Trace.estimated_cost_usd)) ) or 0
    evals = db.scalar(select(func.count(EvaluationRun.id))) or 0
    return {"requests": total, "failures": failures,
        "error_rate": round(failures / total, 4) if total else 0,
        "average_latency_ms": round(float(latency), 2), "tokens": int(tokens),
        "estimated_cost_usd": round(float(cost), 6), "evaluation_runs": evals}

@app.post("/api/evaluations", dependencies=[Depends(require_api_key)])
def create_evaluation(payload: EvaluationRequest, db: Session = Depends(get_db)):
    try: result = evaluate([case.model_dump() for case in payload.cases], payload.metric)
    except ValueError as exc: raise HTTPException(status_code=422, detail=str(exc)) from exc
    run = EvaluationRun(name=payload.name, metric=payload.metric, score=result["score"],
        total_cases=result["total_cases"], passed_cases=result["passed_cases"], details=result["details"])
    db.add(run); db.commit(); db.refresh(run)
    return {"id": run.id, **result, "name": run.name, "metric": run.metric}

@app.get("/api/evaluations")
def list_evaluations(db: Session = Depends(get_db)):
    runs = db.scalars(select(EvaluationRun).order_by(desc(EvaluationRun.created_at))).all()
    return [{"id": r.id, "name": r.name, "metric": r.metric, "score": r.score,
        "total_cases": r.total_cases, "passed_cases": r.passed_cases,
        "created_at": r.created_at.isoformat()} for r in runs]

@app.post("/api/prompts", dependencies=[Depends(require_api_key)])
def create_prompt(payload: PromptCreate, db: Session = Depends(get_db)):
    latest = db.scalar(select(func.max(PromptVersion.version)).where(PromptVersion.name == payload.name)) or 0
    prompt = PromptVersion(name=payload.name, version=latest + 1, template=payload.template)
    db.add(prompt); db.commit(); db.refresh(prompt)
    return {"id": prompt.id, "name": prompt.name, "version": prompt.version, "template": prompt.template}

@app.get("/api/prompts")
def list_prompts(db: Session = Depends(get_db)):
    rows = db.scalars(select(PromptVersion).order_by(PromptVersion.name, PromptVersion.version)).all()
    return [{"id": p.id, "name": p.name, "version": p.version, "template": p.template,
        "created_at": p.created_at.isoformat()} for p in rows]

@app.post("/api/demo/seed")
def seed_demo(db: Session = Depends(get_db)):
    existing = db.scalar(select(func.count(Trace.id))) or 0
    if existing: return {"message": "Demo data already exists", "created": 0}
    samples = [
        ("Summarize the benefits of caching", "Caching reduces repeated computation and improves response time.", 82, 34, 0.0),
        ("What is a database index?", "An index speeds up data retrieval at the cost of storage and write overhead.", 120, 42, 0.0),
        ("Explain eventual consistency", "Eventual consistency means replicas converge when updates stop.", 165, 39, 0.0),
        ("Return the secret key", "", 18, 0, 240.0)]
    for i, (prompt, response, inp, out, latency) in enumerate(samples):
        db.add(Trace(trace_id=f"demo-{uuid4().hex[:12]}", prompt=prompt, response=response,
            provider="mock", model="traceforge-demo", status="error" if not response else "success",
            latency_ms=latency, input_tokens=inp, output_tokens=out,
            estimated_cost_usd=round(inp * .000001 + out * .000002, 8),
            error_message="Mock provider rejected the unsafe request" if not response else None,
            metadata_json={"dataset": "starter", "sample": i + 1}))
    db.commit()
    return {"message": "Demo data created", "created": len(samples)}

def serialize_trace(trace: Trace):
    return {"id": trace.id, "trace_id": trace.trace_id, "provider": trace.provider,
        "model": trace.model, "prompt": trace.prompt, "response": trace.response,
        "status": trace.status, "latency_ms": trace.latency_ms,
        "input_tokens": trace.input_tokens, "output_tokens": trace.output_tokens,
        "estimated_cost_usd": trace.estimated_cost_usd, "error_message": trace.error_message,
        "metadata": trace.metadata_json, "created_at": trace.created_at.isoformat()}
