"""LangGraph node function for the summarization service."""

from typing import Any, Dict

from .config import SummarizerConfig
from .models import SummarizationInput
from .service import SummarizationService
from state import State


class SummarizationNode:
    """LangGraph-like node wrapper for task summarization."""

    def __init__(self, llm: Any | None = None, config: SummarizerConfig | None = None):
        self.service = SummarizationService(llm=llm, config=config)

    async def execute(self, state: Dict[str, Any]) -> Dict[str, Any]:
        from state import State

        current_state = State(**state)

        tasks_to_summarize = [
            task for task in current_state.todos
            if task.search_results and task.status in {"in_progress", "pending"}
        ]

        if not tasks_to_summarize:
            return {"progress_logs": ["⚠ No tasks to summarize"], "current_stage": "summarizing"}

        inputs = [
            SummarizationInput(
                task_id=task.id,
                task_title=task.title,
                task_intent=task.intent,
                task_query=task.query,
                search_results=task.search_results,
            )
            for task in tasks_to_summarize
        ]

        results = await self.service.summarize_batch(inputs)

        completed_tasks = []
        task_summaries = {}

        for result in results:
            if result.success:
                task = next(t for t in tasks_to_summarize if t.id == result.task_id)
                task.summary = result.summary
                task.sources = result.sources
                task.status = "completed"
                completed_tasks.append(task)
                task_summaries[result.task_id] = result.summary

        progress_log = f"✓ Summarized {len(completed_tasks)} tasks"

        return {
            "completed_todos": completed_tasks,
            "task_summaries": task_summaries,
            "progress_logs": [progress_log],
            "current_stage": "summarizing",
        }
    