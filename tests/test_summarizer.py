import pytest

from Summarizer.models import SummarizationInput
from Summarizer.service import SummarizationService
from state import State, TodoItem


class FakeLLM:
    async def ainvoke(self, prompt: str) -> str:
        return "This summary covers the core findings. See https://example.com/guide for details. Additional context is available at https://example.com/research."


@pytest.mark.asyncio
async def test_summarization_service_runs_without_external_agents():
    service = SummarizationService(llm=FakeLLM())
    result = await service.summarize(
        SummarizationInput(
            task_id="task-1",
            task_title="Website performance review",
            task_intent="Find the main performance issues and recommended fixes",
            task_query="website performance optimization",
            search_results=[
                {"title": "Performance Guide", "url": "https://example.com/guide", "snippet": "Caching and CDN improve speed."},
                {"title": "Research Notes", "url": "https://example.com/research", "snippet": "Use lazy loading to reduce initial payload."},
            ],
        )
    )

    assert result.success is True
    assert result.task_id == "task-1"
    assert len(result.summary) > 40
    assert "https://example.com/guide" in result.sources
    assert result.word_count > 0


def test_state_and_todo_model_are_valid():
    item = TodoItem(
        id="t1",
        title="Analyze results",
        intent="Understand the performance issues",
        query="website speed",
        status="in_progress",
        search_results=[{"title": "Example", "url": "https://example.com"}],
    )
    state = State(todos=[item])

    assert state.todos[0].id == "t1"
    assert state.todos[0].status == "in_progress"
