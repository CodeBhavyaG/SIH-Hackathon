import argparse
import asyncio
import json

from Summarizer.models import SummarizationInput
from Summarizer.service import SummarizationService

DEFAULT_TASK = {
    "task_title": "Website performance review",
    "task_intent": "Find the main performance issues and practical fixes for a slow website.",
    "task_query": "website performance optimization best practices",
    "search_results": [
        {
            "title": "Core Web Vitals Overview",
            "url": "https://example.com/performance",
            "snippet": "Slow loading pages hurt conversion and user satisfaction. Optimizing LCP, CLS, and INP improves user experience.",
        },
        {
            "title": "Caching and CDN Best Practices",
            "url": "https://example.com/cache",
            "snippet": "Caching static assets and using a CDN reduces latency and improves response time across regions.",
        },
        {
            "title": "Frontend Delivery Guide",
            "url": "https://example.com/frontend",
            "snippet": "Deferring non-critical scripts, compressing images, and reducing bundle size are key optimization strategies.",
        },
    ],
}


async def run_task(task_data: dict):
    service = SummarizationService()
    result = await service.summarize(
        SummarizationInput(
            task_id="demo-task",
            task_title=task_data["task_title"],
            task_intent=task_data["task_intent"],
            task_query=task_data["task_query"],
            search_results=task_data["search_results"],
        )
    )

    print("SUCCESS:", result.success)
    print("WORD_COUNT:", result.word_count)
    print("SOURCES:")
    for source in result.sources:
        print(" -", source)
    print("\nSUMMARY:\n")
    print(result.summary)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run one summarizer test task.")
    parser.add_argument("--task-title", default=DEFAULT_TASK["task_title"])
    parser.add_argument("--intent", default=DEFAULT_TASK["task_intent"])
    parser.add_argument("--query", default=DEFAULT_TASK["task_query"])
    parser.add_argument(
        "--results-json",
        default=json.dumps(DEFAULT_TASK["search_results"]),
        help="JSON array of search result objects with title, url, and snippet",
    )
    args = parser.parse_args()

    task_data = {
        "task_title": args.task_title,
        "task_intent": args.intent,
        "task_query": args.query,
        "search_results": json.loads(args.results_json),
    }

    asyncio.run(run_task(task_data))
