# SuperBeing

A runnable multi-LLM orchestration backend built with FastAPI. It provides one consistent `/chat` API for GPT-4o, Claude, and Gemini, and is structured for future RAG, memory, agent, and workflow chunks.

## Included in Day 1 and Day 2

- FastAPI app with interactive Swagger documentation at `/docs`
- `/health` endpoint reports configured providers
- `/chat` accepts a provider, prompt, system prompt, temperature, and token limit
- Adapters for OpenAI GPT-4o, Anthropic Claude, and Google Gemini
- Environment-based API-key management; no secret is committed
- Optional `X-API-Key` protection for `/chat`
- Smoke tests for health, docs, and missing-key behavior
- Streamlit interface with simple chat and a Multi-Agent Workflow tab
- Task decomposition, rule-based routing, and a sequential Planner → Executor → Verifier workflow

## Day 2 workflow

For a complex request, SuperBeing makes exactly three required LLM calls:

1. **Planner** asks for a JSON plan of 1–3 tasks. If the response is invalid JSON, it safely uses the original request as one task.
2. **Executor** creates a useful draft for the first planned task.
3. **Verifier** improves clarity and coverage of that draft. It does not fact-check or browse the web.

The API returns the final answer, generated plan, routing decisions, and a visible workflow trace.

### Rule-based routing

This routing is transparent **rule-based logic, not machine learning**. In Auto mode the preferred provider is selected if its API key is configured; otherwise the router deterministically falls back to another configured provider and records why.

| Task type / intent | Preferred provider |
| --- | --- |
| analysis, comparison, evaluation | Anthropic |
| summarization, long explanation, document-style response | Gemini |
| writing, general question, creative response | OpenAI |

An explicit user selection overrides Auto mode, but must have a configured API key.

### Workflow API

`POST /api/v1/workflow`

~~~json
{
  "message": "Compare Java and Python for backend development.",
  "provider": "auto"
}
~~~

The valid provider values are `auto`, `openai`, `anthropic`, and `gemini`. Open `/docs` to test this endpoint interactively.

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

In a second terminal, launch the interface with:

~~~powershell
streamlit run streamlit_app.py
~~~

## Not implemented yet

RAG/document upload, web search, persistent memory, databases, authentication, Docker, React, cloud deployment, parallel agents, and autonomous agents are intentionally later milestones.

## Security

Never commit the `.env` file or API keys. Copy `.env.example` and fill only keys you own.
