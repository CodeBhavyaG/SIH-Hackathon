from pydantic import BaseModel
from typing import TypedDict

class State(BaseModel):
    """
    State class to represent the state of the application.
    """
    # Add your state attributes here
    query: str


class ResearchTask(TypedDict):
  task_description: str
  assigned_agent: str
  status: str = "pending"
  result: str | None = None

class SupervisorState(BaseModel):
  research_brief: str
  tasks: list[ResearchTask] = []
  final_summary: str | None = None
