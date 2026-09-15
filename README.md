# SuperBeing

A runnable multi-LLM orchestration backend built with FastAPI. It provides one consistent `/chat` API for GPT-4o, Claude, and Gemini, and is structured for future RAG, memory, agent, and workflow chunks.

## Included in Chunks 1–2

- FastAPI app with interactive Swagger documentation at `/docs`
- `/health` endpoint reports configured providers
- `/chat` accepts a provider, prompt, system prompt, temperature, and token limit
- Adapters for OpenAI GPT-4o, Anthropic Claude, and Google Gemini
- Environment-based API-key management; no secret is committed
- Optional `X-API-Key` protection for `/chat`
- Smoke tests for health, docs, and missing-key behavior

## Run locally (Windows PowerShell)

~~~powershell
git clone https://github.com/charvijain17/SuperBeing.git
cd SuperBeing
git checkout setup/chunks-1-2-fastapi
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
~~~

Open http://127.0.0.1:8000/docs. `/health` works immediately. To make a real `/chat` request, place the relevant key in `.env`, restart Uvicorn, and use this Swagger body:

~~~json
{
  "provider": "openai",
  "prompt": "Explain database normalization in simple words.",
  "temperature": 0.3,
  "max_tokens": 250
}
~~~

Supported providers: `openai`, `anthropic`, `gemini`.

## Security

Never commit the `.env` file or API keys. Copy `.env.example` and fill only keys you own.
