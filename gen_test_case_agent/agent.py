import json
from typing import Any, List, TypedDict
from langgraph.graph import StateGraph, END, START
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_client import llm_client
from gen_test_case_agent.prompts import TestCaseCreatePrompt
from gen_test_case_agent import schemas
from typing import Annotated


def append_reducer(old_list: List[Any], new_items: Any) -> List[Any]:
    """将新内容追加到列表的合并函数"""
    if old_list is None:
        old_list = []
    if new_items is None:
        return old_list
    # 如果新内容本身是列表，则扩展
    if isinstance(new_items, list):
        if old_list:
            return old_list + new_items
        return new_items
    # 否则作为单个元素追加
    if old_list:
        return old_list + [new_items]
    return [new_items]


class GenTestCaseState(TypedDict):
    trm_text: str
    status: str
    test_case: Annotated[List[Any], append_reducer]
    messages: Annotated[List[BaseMessage], add_messages]


def create(state: GenTestCaseState):
    print("creating")
    parser = JsonOutputParser(pydantic_object=schemas.TestSchema)
    resp = llm_client.run_prompt(system_prompt=TestCaseCreatePrompt.system_prompt,
                                 user_prompt=TestCaseCreatePrompt.user_prompt,
                                 input={"trm_json": state["trm_text"]},
                                 parser=parser)
    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)
    return {"test_case": result}


def save(state: GenTestCaseState):
    """ save to json"""
    print("saving")
    with open('test_case.json', 'w', encoding='utf-8') as f:
        json.dump(state["test_case"], f, indent=4, ensure_ascii=False)


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(GenTestCaseState)

    # 添加节点
    workflow.add_node("create_task", create)
    workflow.add_node("save_task", save)

    # 任务
    workflow.add_edge(START, "create_task")
    workflow.add_edge("create_task", "save_task")
    workflow.add_edge("save_task", END)

    # 编译图
    graph = workflow.compile()

    # 打印图结构
    print("图结构:")
    print(graph.get_graph().draw_mermaid())

    return graph


def run_graph(input):
    print("=" * 50)
    print("LangGraph并行执行开始")
    print("=" * 50)
    # 创建初始状态
    initial_state = GenTestCaseState(
        trm_text=input,
        test_case=[],
        messages=[]
    )
    graph = create_graph()
    print("\n开始执行工作流...")
    print("-" * 50)
    final_state = graph.invoke(initial_state)
    print(final_state)
    print(final_state["test_case"])
