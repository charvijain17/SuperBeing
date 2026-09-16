"""Planner agent: creates a short structured plan from a user request."""

import json

from app.schemas import PlanTask


def parse_plan(raw_text: str, original_query: str) -> list[PlanTask]:
    """Parse LLM JSON safely; use one clear task whenever parsing fails."""
    try:
        data = json.loads(raw_text)
        if not isinstance(data, list) or not 1 <= len(data) <= 3:
            raise ValueError("Plan must be a list with one to three tasks.")
        tasks = [PlanTask(**item) for item in data]
        return tasks
    except (json.JSONDecodeError, TypeError, ValueError):
        return [PlanTask(task_id=1, description=original_query, task_type="general question")]


def planner_prompt(query: str) -> str:
    return f'''Create a compact plan for this user request: {query!r}

Return ONLY valid JSON: a list of 1 to 3 objects with task_id (integer), description (string), and task_type.
Choose task_type from analysis, comparison, evaluation, summarization, long explanation, document-style response, writing, general question, or creative response.'''
