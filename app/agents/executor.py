"""Executor agent: produces a useful draft using one selected provider."""

from app.schemas import PlanTask


def executor_prompt(query: str, plan: list[PlanTask], current_task: PlanTask) -> str:
    plan_text = "\n".join(f"{task.task_id}. {task.description} ({task.task_type})" for task in plan)
    return f'''Answer the user's request helpfully and concisely.

Original request: {query}
Plan:\n{plan_text}
Current task: {current_task.description}

Produce a complete draft answer. Do not mention internal agents or routing.'''
