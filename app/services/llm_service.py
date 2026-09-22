"""One normalized interface over OpenAI, Anthropic, and Gemini."""
from dataclasses import dataclass
from app.config import Settings
from app.schemas import ChatRequest, ProviderName

class ProviderNotConfiguredError(Exception):
    pass


def has_api_key(value: str | None) -> bool:
    """Return true only for a non-empty, non-whitespace API key."""
    return bool(value and value.strip())

@dataclass
class ProviderResult:
    provider: ProviderName
    model: str
    content: str

class OpenAIProvider:
    def __init__(self, settings: Settings): self.settings = settings
    def generate(self, request: ChatRequest) -> ProviderResult:
        if not has_api_key(self.settings.openai_api_key): raise ProviderNotConfiguredError("OPENAI_API_KEY is not configured.")
        from openai import OpenAI
        response = OpenAI(api_key=self.settings.openai_api_key).chat.completions.create(model=self.settings.openai_model, messages=[{"role":"system","content":request.system_prompt or ""},{"role":"user","content":request.prompt}], temperature=request.temperature, max_tokens=request.max_tokens)
        return ProviderResult(ProviderName.openai, self.settings.openai_model, response.choices[0].message.content or "")

class AnthropicProvider:
    def __init__(self, settings: Settings): self.settings = settings
    def generate(self, request: ChatRequest) -> ProviderResult:
        if not has_api_key(self.settings.anthropic_api_key): raise ProviderNotConfiguredError("ANTHROPIC_API_KEY is not configured.")
        import anthropic
        message = anthropic.Anthropic(api_key=self.settings.anthropic_api_key).messages.create(model=self.settings.anthropic_model, system=request.system_prompt or "", messages=[{"role":"user","content":request.prompt}], temperature=request.temperature, max_tokens=request.max_tokens)
        return ProviderResult(ProviderName.anthropic, self.settings.anthropic_model, "".join(block.text for block in message.content if block.type == "text"))

class GeminiProvider:
    def __init__(self, settings: Settings): self.settings = settings
    def generate(self, request: ChatRequest) -> ProviderResult:
        if not has_api_key(self.settings.google_api_key): raise ProviderNotConfiguredError("GOOGLE_API_KEY is not configured.")
        from google import genai
        from google.genai import types
        response = genai.Client(api_key=self.settings.google_api_key).models.generate_content(model=self.settings.gemini_model, contents=request.prompt, config=types.GenerateContentConfig(system_instruction=request.system_prompt, temperature=request.temperature, max_output_tokens=request.max_tokens))
        return ProviderResult(ProviderName.gemini, self.settings.gemini_model, response.text or "")

def configured_providers(settings: Settings) -> list[ProviderName]:
    keys={ProviderName.openai:settings.openai_api_key, ProviderName.anthropic:settings.anthropic_api_key, ProviderName.gemini:settings.google_api_key}
    return [provider for provider, key in keys.items() if has_api_key(key)]

def generate_response(request: ChatRequest, settings: Settings) -> ProviderResult:
    adapters={ProviderName.openai:OpenAIProvider, ProviderName.anthropic:AnthropicProvider, ProviderName.gemini:GeminiProvider}
    return adapters[request.provider](settings).generate(request)
