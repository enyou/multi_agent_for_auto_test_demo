import json
from datetime import datetime
from operator import add
from typing import TypedDict, List, Dict, Any, Annotated

from langgraph.graph import StateGraph, START
from langgraph.types import Send
from langchain_core.output_parsers import JsonOutputParser

from utils.llm_client import llm_client
from gen_test_code_agent.prompts import (
    UITestCaseStructuredPrompt,
    UITestCaseToCodePrompt
)
from gen_test_code_agent import schemas
from gen_test_code_agent.get_selector_from_html import run as extract_selectors


class GenTestCodeState(TypedDict):
    # ===== 全局输入（只读）=====
    url: str
    test_case_result: List[Dict[str, Any]]

    # ===== fan-out 后，每个 item =====
    test_case: Dict[str, Any]

    # test_code:  Annotated[List[str], add]
    # ===== 共享资源（只执行一次）=====
    page_selector: str

    # ===== fan-in 结果 =====
    test_code_refs: Annotated[List[str], add]


def create_test_code(structured_case, url, selectors=None):
    print("🧪 生成测试代码")

    resp = llm_client.run_prompt(
        system_prompt=UITestCaseToCodePrompt.system_prompt,
        user_prompt=UITestCaseToCodePrompt.user_prompt,
        input={
            "case": structured_case,
            "url": url,
            "selector": selectors
        }
    )

    code = resp.content
    return code


def save_code(case_id, code):
    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_{case_id}_{create_date}.py"
    full_path = f"./test_codes/{file_name}"

    print(f"💾 保存测试代码: {file_name}")

    code = (
        code.replace("```python", "")
            .replace("```", "")
            .strip()
    )

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)


def get_selector_task(state: GenTestCodeState):
    print("🔍 提取页面 selector（仅一次）")
    selectors = extract_selectors(url=state["url"])
    return {
        "page_selector": json.dumps(selectors)
    }


def fan_out_task(state: GenTestCodeState):
    """fan-out 是一个条件边函数，而不是一个节点"""
    print("🔀 fan-out 测试用例")
    return [
        Send(
            "structure_task",
            {"test_case": test_case,
             "url": state["url"],
             "page_selector": state["page_selector"]}
        )
        for test_case in state["test_case_result"]
    ]


def structuring_test_case_node(case_info):
    case_id = case_info['test_case'].get('case_id')
    print(f"🧩 结构化测试用例: {case_id}")

    parser = JsonOutputParser(
        pydantic_object=schemas.UITestCaseSchema
    )

    resp = llm_client.run_prompt(
        system_prompt=UITestCaseStructuredPrompt.sys_prompt,
        user_prompt=UITestCaseStructuredPrompt.user_prompt,
        input={"case": case_info["test_case"]},
        parser=parser
    )

    if not isinstance(resp, str):
        resp = json.dumps(resp, ensure_ascii=False)
    code = create_test_code(resp, case_info["url"], case_info["page_selector"])

    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_{case_id}_{create_date}.py"
    full_path = f"./output/codes/{file_name}"

    print(f"💾 保存测试代码: {file_name}")

    code = (
        code.replace("```python", "")
            .replace("```", "")
            .strip()
    )

    with open(full_path, "w", encoding="utf-8") as f:
        f.write(code)

    return {
        "test_code_refs": [full_path]
    }


def create_graph():
    workflow = StateGraph(GenTestCodeState)

    workflow.add_node("get_selector_task", get_selector_task)
   # workflow.add_node("fan_out_task", fan_out_task)
    workflow.add_node("structure_task", structuring_test_case_node)
    # workflow.add_node("create_code_task", create_test_code_node)
    # workflow.add_node("save_task", save_node)

    # ===== 正确的执行顺序 =====
    workflow.add_edge(START, "get_selector_task")
    # workflow.set_entry_point("fan_out_task")
    # workflow.add_edge("get_selector_task", "fan_out_task")
    # workflow.add_conditional_edges(
    #     START,
    #     fan_out_task
    # )
    workflow.add_conditional_edges(
        "get_selector_task",
        fan_out_task
    )
    # workflow.add_edge("structure_task", "save_task")
    workflow.set_finish_point("structure_task")

    return workflow.compile()


def run_graph(test_cases: List[Dict[str, Any]], url: str):
    graph = create_graph()

    final_state = graph.invoke({
        "url": url,
        "test_case_result": test_cases,
        "test_code_refs": [],
        "page_selector": "",
    })

    print("✅ 生成完成")
    for path in final_state["test_code_refs"]:
        print("  -", path)

    return final_state
