from pydantic import BaseModel, Field


class TraceCreate(BaseModel):
    prompt: str = Field(min_length=1, max_length=20000)
    response: str = ""
    provider: str = "mock"
    model: str = "deterministic-demo"
    status: str = "success"
    latency_ms: float = Field(default=0, ge=0)
    input_tokens: int = Field(default=0, ge=0)
    output_tokens: int = Field(default=0, ge=0)
    error_message: str | None = None
    metadata: dict = Field(default_factory=dict)


class EvaluationCase(BaseModel):
    input: str
    actual: str
    expected: str


class EvaluationRequest(BaseModel):
    name: str = "Untitled evaluation"
    metric: str = "exact_match"
    cases: list[EvaluationCase] = Field(min_length=1, max_length=1000)


class PromptCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    template: str = Field(min_length=1, max_length=20000)
