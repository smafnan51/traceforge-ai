from typing import Any, Literal

from pydantic import BaseModel, Field


class TraceCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=20_000)
    response: str = Field(default="", max_length=20_000)
    provider: str = Field(default="mock", min_length=1, max_length=80)
    model: str = Field(default="deterministic-demo", min_length=1, max_length=120)
    status: Literal["success", "error"] = "success"
    latency_ms: float = Field(default=0, ge=0, le=86_400_000)
    input_tokens: int = Field(default=0, ge=0, le=100_000_000)
    output_tokens: int = Field(default=0, ge=0, le=100_000_000)
    error_message: str | None = Field(default=None, max_length=20_000)
    metadata: dict[str, Any] = Field(default_factory=dict)


class EvaluationCase(BaseModel):
    input: str = Field(max_length=20_000)
    actual: str = Field(max_length=20_000)
    expected: str = Field(max_length=20_000)


class EvaluationRequest(BaseModel):
    name: str = Field(default="Untitled evaluation", min_length=1, max_length=120)
    metric: Literal["exact_match", "normalized_similarity"] = "exact_match"
    cases: list[EvaluationCase] = Field(min_length=1, max_length=1_000)


class PromptCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    template: str = Field(min_length=1, max_length=20_000)
