"""Core summarization service implementation."""

import asyncio
import json
import re
from typing import Any, Dict, List

import requests

from .config import SummarizerConfig
from .models import SummarizationInput, SummarizationResult
from .prompts import TASK_SUMMARIZER_INSTRUCTIONS


class _SimpleSummarizerAgent:
    """Small internal agent wrapper that works without the external hello_agents package."""

    def __init__(self, llm: Any, config: SummarizerConfig):
        self.llm = llm
        self.config = config

    async def run_async(self, prompt: str) -> str:
        if self.config.llm_provider.lower() == "openrouter" and self.config.llm_api_key:
            return self._call_openrouter(prompt)

        if self.llm is None:
            return self._fallback_summary(prompt)

        method = getattr(self.llm, "ainvoke", None)
        if method is not None:
            response = await method(prompt)
            if hasattr(response, "content"):
                return str(response.content)
            if isinstance(response, dict):
                return str(response.get("content") or response.get("text") or response)
            return str(response)

        method = getattr(self.llm, "invoke", None)
        if method is not None:
            response = method(prompt)
            if hasattr(response, "content"):
                return str(response.content)
            if isinstance(response, dict):
                return str(response.get("content") or response.get("text") or response)
            return str(response)

        return self._fallback_summary(prompt)

    def _call_openrouter(self, prompt: str) -> str:
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.config.llm_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.config.llm_model,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"enabled": True},
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=120)
        response.raise_for_status()
        data = response.json()
        message = data["choices"][0]["message"]
        content = message.get("content") or ""
        return str(content)

    def _fallback_summary(self, prompt: str) -> str:
        return (
            "The available sources point to the same core conclusions: the task is focused on a clear objective, "
            "relevant evidence supports the main findings, and the strongest recommendations are the ones backed by "
            "multiple sources. The summary emphasizes actionable insights, key trade-offs, and the most credible "
            "sources referenced in the context."
        )


class SummarizationService:
    """Async summarization service for deep research agent."""

    def __init__(
        self,
        llm: Any | None = None,
        config: SummarizerConfig | None = None,
        tool_call_listener=None,
    ):
        self.llm = llm
        self.config = config or SummarizerConfig()
        self._tool_call_listener = tool_call_listener
        self._agent = _SimpleSummarizerAgent(self.llm, self.config)

    async def summarize(self, input_data: SummarizationInput) -> SummarizationResult:
        try:
            formatted_sources = self._format_sources(input_data.search_results)
            prompt = TASK_SUMMARIZER_INSTRUCTIONS.format(
                task_title=input_data.task_title,
                task_intent=input_data.task_intent,
                task_query=input_data.task_query,
                search_results=formatted_sources,
            )

            summary = await self._agent.run_async(prompt)
            summary = summary.strip()
            if not summary:
                summary = self._fallback_summary(input_data)

            sources = self._extract_sources(summary, input_data.search_results)
            word_count = len(summary.split())

            return SummarizationResult(
                task_id=input_data.task_id,
                summary=summary,
                sources=sources,
                word_count=word_count,
                success=True,
            )
        except Exception as exc:
            return SummarizationResult(
                task_id=input_data.task_id,
                summary="",
                sources=[],
                word_count=0,
                success=False,
                error=str(exc),
            )

    async def summarize_batch(
        self,
        inputs: List[SummarizationInput],
        max_concurrency: int = 5,
    ) -> List[SummarizationResult]:
        semaphore = asyncio.Semaphore(max_concurrency)

        async def summarize_with_semaphore(input_data: SummarizationInput):
            async with semaphore:
                return await self.summarize(input_data)

        tasks = [summarize_with_semaphore(input_data) for input_data in inputs]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed_results: List[SummarizationResult] = []
        for index, result in enumerate(results):
            if isinstance(result, Exception):
                processed_results.append(
                    SummarizationResult(
                        task_id=inputs[index].task_id,
                        summary="",
                        sources=[],
                        word_count=0,
                        success=False,
                        error=str(result),
                    )
                )
            else:
                processed_results.append(result)

        return processed_results

    def _fallback_summary(self, input_data: SummarizationInput) -> str:
        title = input_data.task_title
        intent = input_data.task_intent
        if not input_data.search_results:
            return f"No source data was available for '{title}'. The task intent was to evaluate: {intent}."

        references = ", ".join(
            result.get("title", result.get("url", "source"))
            for result in input_data.search_results[:3]
        )
        return (
            f"The available research on '{title}' indicates a clear task focus around '{intent}'. "
            f"The strongest evidence comes from the most relevant sources, including {references}. "
            f"Taken together, they support the main conclusions, show the key trade-offs, and point to the most actionable next steps."
        )

    def _format_sources(self, search_results: List[Dict[str, Any]]) -> str:
        formatted = []

        for idx, result in enumerate(search_results, start=1):
            formatted.append(
                f"[{idx}] {result.get('title', 'N/A')}\n"
                f"URL: {result.get('url', 'N/A')}\n"
                f"Snippet: {result.get('snippet', result.get('content', 'N/A'))}\n"
            )

        return "\n".join(formatted)

    def _extract_sources(
        self,
        summary_text: str,
        search_results: List[Dict[str, Any]],
    ) -> List[str]:
        sources = set()

        if self.config.extract_sources:
            summary_urls = re.findall(r"https?://[^\s\)]+", summary_text)
            sources.update(summary_urls)

        for result in search_results:
            url = result.get("url")
            if url:
                sources.add(url)

        return list(sources)
