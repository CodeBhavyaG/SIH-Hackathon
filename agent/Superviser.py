from langchain_groq import ChatGroq
from dotenv import load_dotenv
import os

from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain.agents import create_agent
import json
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


system_prompt = """You are a Supervisor agent. Your primary task is to decompose a given research brief into specific, manageable subtopics. You have three hypothetical agents ('ResearchAgent_1', 'ResearchAgent_2', or 'ResearchAgent_3') delegate subtopics to them ,if there are more then 3 subtopics that are made then you can give more then one subtopic to the same agent but make sure that the subtopics that are given to the same agent are related so it can have similar context for all the subtopic.

Don’t delegate all the tasks to one agent if the topics are related keep a balance between load and delegation suppose ResearchAgent_2 is working on 3 topics and ResearchAgent_3 and ResearchAgent_1 are working on none then prioritise giving task to them rather then overloading  ResearchAgent_2 with work

<output_structure>
{ "research_brief": "string", "tasks": [ { "task_description": "string", "assigned_agent": "string", "status": "pending","result": null } ], "final_summary": null }
</output_structure>"""

message = []

agent = create_agent(model=llm, tools=[], system_prompt=SystemMessage(system_prompt), response_format=SupervisorState)
response = agent.invoke({"messages": [HumanMessage("what is the meaning of life?")]})
