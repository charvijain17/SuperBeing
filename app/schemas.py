"""HTTP models shared by endpoints and LLM adapters."""
from enum import Enum
from pydantic import BaseModel, Field

class ProviderName(str, Enum):
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
