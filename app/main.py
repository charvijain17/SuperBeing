"""FastAPI entry point for SuperBeing."""
from secrets import compare_digest, token_urlsafe
from fastapi import Depends, FastAPI, Header, HTTPException, status
from app.config import Settings, get_settings
from app.schemas import ChatRequest, ChatResponse, HealthResponse
from app.services.llm_service import ProviderNotConfiguredError, configured_providers, generate_response

settings=get_settings()
app=FastAPI(title=settings.app_name, version=settings.app_version, description="A multi-LLM orchestration API. Select OpenAI, Anthropic, or Gemini per request.")

def require_api_key(x_api_key: str | None = Header(default=None, description="Optional server API key"), current_settings: Settings = Depends(get_settings)) -> None:
    if current_settings.app_api_key and not (x_api_key and compare_digest(x_api_key, current_settings.app_api_key)):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or missing X-API-Key.")

@app.get("/", tags=["System"])
def root() -> dict[str,str]:
    return {"message":"SuperBeing API is running. Open /docs to try it."}

@app.get("/health", response_model=HealthResponse, tags=["System"])
def health(current_settings: Settings = Depends(get_settings)) -> HealthResponse:
    return HealthResponse(status="ok", app=current_settings.app_name, version=current_settings.app_version, configured_providers=configured_providers(current_settings))

@app.post("/chat", response_model=ChatResponse, tags=["Chat"], dependencies=[Depends(require_api_key)])
def chat(request: ChatRequest, current_settings: Settings = Depends(get_settings)) -> ChatResponse:
    try:
        result=generate_response(request, current_settings)
    except ProviderNotConfiguredError as error:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(error)) from error
    except Exception as error:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=f"Provider request failed: {error}") from error
    return ChatResponse(provider=result.provider, model=result.model, content=result.content, request_id=token_urlsafe(12))
