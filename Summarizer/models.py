"""Data models for the summarization service."""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field


class SummarizationInput(BaseModel):
    """
    Input model for the summarization service.
    
    This wraps the TodoItem and search results into a single input object.
    """
    
    task_id: str = Field(..., description="Unique task identifier")
    task_title: str = Field(..., description="Task title")
    task_intent: str = Field(..., description="Task intent/description")
    task_query: str = Field(..., description="Search query for this task")
    search_results: List[Dict[str, Any]] = Field(
        ...,
        description="Raw search results from search API"
    )


class SummarizationResult(BaseModel):
    """
    Output model from the summarization service.
    
    Contains the summary text and extracted sources.
    """
    
    task_id: str = Field(..., description="Task identifier (matches input)")
    summary: str = Field(..., description="Generated summary text")
    sources: List[str] = Field(
        default_factory=list,
        description="List of source URLs"
    )
    word_count: int = Field(
        default=0,
        description="Number of words in summary"
    )
    success: bool = Field(
        default=True,
        description="Whether summarization succeeded"
    )
    error: Optional[str] = Field(
        None,
        description="Error message if summarization failed"
    )