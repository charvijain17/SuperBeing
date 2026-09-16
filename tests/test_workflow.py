from app.agents.planner import parse_plan
from app.config import Settings
from app.routing.model_router import ModelRouter, NoProviderConfiguredError
from app.schemas import ChatRequest, ProviderName, WorkflowProvider, WorkflowRequest
from app.services.llm_service import ProviderResult
from app.workflows.sequential_workflow import SequentialWorkflow


def settings(**keys):
    return Settings(**keys)


def test_router_prefers_anthropic_for_analysis():
    decision = ModelRouter(settings(anthropic_api_key="a", openai_api_key="o")).route("analysis")
    assert decision.selected_provider == ProviderName.anthropic


def test_router_prefers_gemini_for_summarization():
    decision = ModelRouter(settings(google_api_key="g", openai_api_key="o")).route("summarization")
    assert decision.selected_provider == ProviderName.gemini


def test_router_prefers_openai_for_writing():
    decision = ModelRouter(settings(openai_api_key="o", google_api_key="g")).route("writing")
    assert decision.selected_provider == ProviderName.openai


def test_override_has_priority():
    decision = ModelRouter(settings(openai_api_key="o", anthropic_api_key="a")).route("analysis", WorkflowProvider.openai)
    assert decision.selected_provider == ProviderName.openai
    assert "override" in decision.reason


def test_router_falls_back_safely():
    decision = ModelRouter(settings(google_api_key="g")).route("analysis")
    assert decision.selected_provider == ProviderName.gemini
    assert "fell back" in decision.reason


def test_planner_json_parsing():
    plan = parse_plan('[{"task_id":1,"description":"Compare languages","task_type":"comparison"}]', "ignored")
    assert plan[0].task_type == "comparison"


def test_planner_fallback_for_invalid_json():
    plan = parse_plan("not json", "Original request")
    assert plan[0].description == "Original request"


def fake_generator(request: ChatRequest, _settings: Settings) -> ProviderResult:
    if "Return ONLY valid JSON" in request.prompt:
        content = '[{"task_id":1,"description":"Compare Java and Python.","task_type":"comparison"}]'
    elif "Improve the draft" in request.prompt:
        content = "Java is often preferred for large enterprise backends; Python is faster for rapid development."
    else:
        content = "Java is strict and scalable; Python is concise and productive."
    return ProviderResult(provider=request.provider, model="mock-model", content=content)


def test_mocked_workflow_returns_complete_trace_and_answer():
    workflow = SequentialWorkflow(settings(openai_api_key="o", anthropic_api_key="a"), generator=fake_generator)
    response = workflow.run(WorkflowRequest(message="Compare Java and Python.", provider="auto"))
    assert [entry.agent for entry in response.workflow_trace] == ["Planner", "Executor", "Verifier"]
    assert response.final_answer
    assert response.workflow_trace[1].provider == ProviderName.anthropic


def test_no_provider_is_controlled_error():
    try:
        ModelRouter(settings()).route("analysis")
    except NoProviderConfiguredError as error:
        assert "No LLM provider is configured" in str(error)
    else:
        raise AssertionError("Expected friendly configuration error")
