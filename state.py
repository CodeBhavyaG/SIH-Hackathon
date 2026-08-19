from typing import Any, Dict, List

from pydantic import BaseModel, Field, ConfigDict


class TodoItem(BaseModel):
    """A single task item in the project workflow."""

    model_config = ConfigDict(extra="allow")

    id: str
    title: str
    intent: str
    query: str
    status: str = "pending"
    search_results: List[Dict[str, Any]] = Field(default_factory=list)
    summary: str = ""
    sources: List[str] = Field(default_factory=list)


class State(BaseModel):
    """Application state for graph-based task processing."""

    model_config = ConfigDict(extra="allow")

    todos: List[TodoItem] = Field(default_factory=list)
    completed_todos: List[TodoItem] = Field(default_factory=list)
    task_summaries: Dict[str, str] = Field(default_factory=dict)
    progress_logs: List[str] = Field(default_factory=list)
    current_stage: str = "idle"
    query: str = ""
