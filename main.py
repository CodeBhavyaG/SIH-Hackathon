import asyncio

from Summarizer.models import SummarizationInput
from Summarizer.service import SummarizationService


async def demo_summary():
    service = SummarizationService()
    input_data = SummarizationInput(
        task_id="demo-1",
        task_title="Improve website performance",
        task_intent="Find the root causes of slow page loads and the practical fixes",
        task_query="website speed optimization",
        search_results=[
            {
                "title": "Core Web Vitals Overview",
                "url": "https://example.com/performance",
                "snippet": "Largest contentful paint and CLS are critical user experience metrics.",
            },
            {
                "title": "Frontend Optimization Guide",
                "url": "https://example.com/frontend",
                "snippet": "Deferring non-essential scripts and using caching helps reduce time to first paint.",
            },
        ],
    )

    result = await service.summarize(input_data)
    print("Summary:")
    print(result.summary)
    print("Sources:", result.sources)


def main():
    print("Starting summarizer demo...")
    asyncio.run(demo_summary())


if __name__ == "__main__":
    main()

