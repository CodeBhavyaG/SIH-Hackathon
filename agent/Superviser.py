import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain.messages import SystemMessage
from langchain_groq import ChatGroq

project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from state import SupervisorState

load_dotenv()
api_key = os.getenv("api_key")

llm = ChatGroq(
    model_name="qwen/qwen3.6-27b",
    api_key=api_key,
    temperature=0.1,
    # max_tokens=6000,
    reasoning_effort="none",  # "default"
    # CRITICAL: ReAct/Tool agents require reasoning to be parsed or hidden,
    # otherwise raw <think> tags will break the parser layout.
    reasoning_format="parsed",
)


prompt_path = project_root / "prompt" / "Superviser.md"
system_prompt = prompt_path.read_text(encoding="utf-8")

message = []

print("System Prompt:")
print(system_prompt)

agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=SystemMessage(system_prompt),
    response_format=SupervisorState,
)
