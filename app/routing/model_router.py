"""A small, explainable rule-based model router; it does not use ML."""

from app.config import Settings
from app.schemas import ProviderName, RoutingDecision, WorkflowProvider
from app.services.llm_service import configured_providers


class NoProviderConfiguredError(Exception):
    """Raised when no provider API key is available for a workflow."""


class ModelRouter:
    """Routes by task category with deterministic preference and fallback rules."""

    preferred_by_task_type = {
        "analysis": ProviderName.anthropic,
        "comparison": ProviderName.anthropic,
        "evaluation": ProviderName.anthropic,
        "summarization": ProviderName.gemini,
        "long explanation": ProviderName.gemini,
        "document-style response": ProviderName.gemini,
        "writing": ProviderName.openai,
        "general question": ProviderName.openai,
        "creative response": ProviderName.openai,
    }
    fallback_order = [ProviderName.openai, ProviderName.anthropic, ProviderName.gemini]

    def __init__(self, settings: Settings):
        self.settings = settings

    def route(self, task_type: str, override: WorkflowProvider = WorkflowProvider.auto) -> RoutingDecision:
        available = configured_providers(self.settings)
        if not available:
            raise NoProviderConfiguredError(
                "No LLM provider is configured. Add an OPENAI_API_KEY, ANTHROPIC_API_KEY, or GOOGLE_API_KEY to .env."
            )

        normalized_type = task_type.strip().lower()
        if override != WorkflowProvider.auto:
            selected = ProviderName(override.value)
            if selected not in available:
                raise NoProviderConfiguredError(
                    f"{selected.value.title()} was selected, but its API key is not configured. Choose Auto or configure that provider."
                )
            return self._decision(normalized_type, selected, f"User selected {selected.value.title()} as an override.")

        preferred = self.preferred_by_task_type.get(normalized_type, ProviderName.openai)
        if preferred in available:
            return self._decision(normalized_type, preferred, f"{self._label(preferred)} is the rule-based preference for {normalized_type} tasks.")

        fallback = next(provider for provider in self.fallback_order if provider in available)
        return self._decision(
            normalized_type,
            fallback,
            f"{self._label(preferred)} is preferred for {normalized_type} tasks but is not configured; fell back to {self._label(fallback)}.",
        )

    def _decision(self, task_type: str, provider: ProviderName, reason: str) -> RoutingDecision:
        models = {
            ProviderName.openai: self.settings.openai_model,
            ProviderName.anthropic: self.settings.anthropic_model,
            ProviderName.gemini: self.settings.gemini_model,
        }
        return RoutingDecision(task_type=task_type, selected_provider=provider, model=models[provider], reason=reason)

    @staticmethod
    def _label(provider: ProviderName) -> str:
        return {ProviderName.openai: "OpenAI", ProviderName.anthropic: "Anthropic", ProviderName.gemini: "Gemini"}[provider]
