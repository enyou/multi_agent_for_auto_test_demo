from langgraph.graph import START, END, StateGraph
from typing import TypedDict,  Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import MessagesState

from gen_test_case_agent.agent import create_graph as test_case_create_agent
from gen_test_code_agent.agent import create_graph as test_code_create_agent
from requirement_analyzer_agent.agent import create_graph as trm_create_agent


class GrobalState(TypedDict):
    user_input: str
    trm_result: str
    test_case_result: str
    test_code_result: str


graph = StateGraph(MessagesState)

