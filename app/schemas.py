"""HTTP models shared by endpoints and LLM adapters."""
from enum import Enum
from pydantic import BaseModel, Field

class ProviderName(str, Enum):
    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"


class WorkflowProvider(str, Enum):
    auto = "auto"
    openai = "openai"
    anthropic = "anthropic"
    gemini = "gemini"

class ChatRequest(BaseModel):
    provider: ProviderName
    prompt: str = Field(min_length=1, max_length=12000)
    system_prompt: str | None = Field(default="You are SuperBeing, a helpful AI assistant.", max_length=4000)
    temperature: float = Field(default=0.3, ge=0, le=1)
    max_tokens: int = Field(default=700, ge=1, le=4000)

class ChatResponse(BaseModel):
    provider: ProviderName
    model: str
    content: str
    request_id: str

class HealthResponse(BaseModel):
    status: str
    app: str
    version: str
    configured_providers: list[ProviderName]


class PlanTask(BaseModel):
    task_id: int = Field(ge=1)
    description: str = Field(min_length=1)
    task_type: str = Field(min_length=1)


class RoutingDecision(BaseModel):
    task_type: str
    selected_provider: ProviderName
    model: str
    reason: str


class WorkflowTraceEntry(BaseModel):
    step: int
    agent: str
    status: str
    provider: ProviderName
    model: str
    summary: str
    intermediate_draft: str | None = None


class WorkflowRequest(BaseModel):
    message: str = Field(min_length=1, max_length=12000)
    provider: WorkflowProvider = WorkflowProvider.auto


class WorkflowResponse(BaseModel):
    final_answer: str
    plan: list[PlanTask]
    workflow_trace: list[WorkflowTraceEntry]
    routing_decisions: list[RoutingDecision]
