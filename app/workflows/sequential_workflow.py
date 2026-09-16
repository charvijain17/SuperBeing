"""Planner -> Executor -> Verifier workflow using exactly three model calls."""

from collections.abc import Callable

from app.agents.executor import executor_prompt
from app.agents.planner import parse_plan, planner_prompt
from app.agents.verifier import verifier_prompt
from app.config import Settings
from app.routing.model_router import ModelRouter
from app.schemas import ChatRequest, WorkflowProvider, WorkflowRequest, WorkflowResponse, WorkflowTraceEntry
from app.services.llm_service import ProviderResult, generate_response

Generator = Callable[[ChatRequest, Settings], ProviderResult]


class SequentialWorkflow:
    def __init__(self, settings: Settings, generator: Generator = generate_response):
        self.settings = settings
        self.generator = generator
        self.router = ModelRouter(settings)

    def run(self, request: WorkflowRequest) -> WorkflowResponse:
        planner_route = self.router.route("general question", request.provider)
        plan_result = self._generate(planner_route.selected_provider, planner_prompt(request.message))
        plan = parse_plan(plan_result.content, request.message)

        execution_route = self.router.route(plan[0].task_type, request.provider)
        draft_result = self._generate(execution_route.selected_provider, executor_prompt(request.message, plan, plan[0]))

        # Reuse the executor's selected provider for verification: three calls total.
        verified_result = self._generate(execution_route.selected_provider, verifier_prompt(request.message, draft_result.content))
        trace = [
            WorkflowTraceEntry(step=1, agent="Planner", status="completed", provider=plan_result.provider, model=plan_result.model, summary=f"Created {len(plan)} task(s)."),
            WorkflowTraceEntry(step=2, agent="Executor", status="completed", provider=draft_result.provider, model=draft_result.model, summary=f"Completed {plan[0].task_type} task.", intermediate_draft=draft_result.content),
            WorkflowTraceEntry(step=3, agent="Verifier", status="completed", provider=verified_result.provider, model=verified_result.model, summary="Reviewed and improved the final response."),
        ]
        return WorkflowResponse(final_answer=verified_result.content, plan=plan, workflow_trace=trace, routing_decisions=[planner_route, execution_route])

    def _generate(self, provider, prompt: str) -> ProviderResult:
        return self.generator(ChatRequest(provider=provider, prompt=prompt), self.settings)
