from datetime import datetime
import json
from typing import Any, Dict, List, Optional, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_client import llm_client
from gen_test_case_agent.prompts import TestCaseCreatePrompt
from gen_test_case_agent import schemas
from state import GlobalState

class TestCase(TypedDict):
    """
    测试case生成的agent状态
    """
    case_id: str
    title: str
    type: str
    preconditions: str
    steps: List[str]
    inputs: Dict[str, str]
    expected_results: str
    priority: str

class TestCaseState(TypedDict):
    """状态定义"""
    trm_result: Dict[str, Any]
    test_case_result: Optional[List[TestCase]]

def create(state: TestCaseState):
    """ create test case"""
    print("creating")
    trm_text = json.dumps(state["doc_parser_result"])
    parser = JsonOutputParser(pydantic_object=schemas.TestSchema)
    resp = llm_client.run_prompt(system_prompt=TestCaseCreatePrompt.system_prompt,
                                 user_prompt=TestCaseCreatePrompt.user_prompt,
                                 input={"trm_json": trm_text},
                                 parser=parser)
    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)
    return {"test_case_result": result}


def save(state: GlobalState):
    """ save to json"""
    print("saving test case")
    feature_id = state["feature_id"]
    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"./output/test_case/test_case_{feature_id}_{create_date}.json"
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(state["test_case_result"], f, indent=4, ensure_ascii=False)


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(GlobalState)

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
