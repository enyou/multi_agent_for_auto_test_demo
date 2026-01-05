import json
import os
from typing import TypedDict
from datetime import datetime
from langgraph.graph import StateGraph, END, START
from langchain_core.output_parsers import JsonOutputParser, StrOutputParser
from utils.llm_client import llm_client
from gen_test_code_agent.prompts import UITestCaseStructuredPrompt, UITestCaseToCodePrompt
from gen_test_code_agent import schemas
from get_selector_from_html import run as extract_selectors


class GenTestCodeState(TypedDict):
    url: str
    test_type: str
    test_case: str
    structured_test_case: str
    page_selector: str
    test_code: str


def structuring_test_case_node(state: GenTestCodeState):
    """
        将自然语言的测试case转化为结构化的测试case
    """
    print("将自然语言的测试case转化为结构化的测试case")
    nlp_test_case = state["test_case"]
    parser = JsonOutputParser(pydantic_object=schemas.UITestCaseSchema)
    resp = llm_client.run_prompt(system_prompt=UITestCaseStructuredPrompt.sys_prompt,
                                 user_prompt=UITestCaseStructuredPrompt.user_prompt,
                                 input={"case": nlp_test_case},
                                 parser=parser)
    print(111111, resp)
    if not isinstance(resp, str):
        return {"structured_test_case": json.dumps(resp)}
    return {"structured_test_case": resp}


def get_selectors_node(state: GenTestCodeState):
    """从页面中提取选择器"""
    selectors = extract_selectors(url=state["url"])
    return {"page_selector": json.dumps(selectors)}


def create_test_code_node(state: GenTestCodeState):
    resp = llm_client.run_prompt(system_prompt=UITestCaseToCodePrompt.system_prompt,
                                 user_prompt=UITestCaseToCodePrompt.user_prompt,
                                 input={"case": state["structured_test_case"],
                                        "url": state["url"],
                                        "selector": state["page_selector"]})
    return {"test_code": resp.content}


def save_node(state: GenTestCodeState):
    """
    将代码字符串保存为Python文件

    参数:
    code_string (str): 要保存的Python代码
    filename (str): 保存的文件名
    """
    print(state["structured_test_case"])
    test_case_dict = json.loads(state["structured_test_case"])
    case_id = test_case_dict["case_id"]
    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    file_name = f"test_{case_id}_{create_date}.py"
    full_path = "./test_codes/{}".format(file_name)
    code = state["test_code"].replace(
        "```python", "").replace("```", "").strip()
    try:
        with open(full_path, 'w', encoding='utf-8') as file:
            file.write(code)
        print(f"代码已成功保存到: {file_name}")
    except Exception as e:
        print(f"保存文件时出错: {e}")


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(GenTestCodeState)

    workflow.add_node("structure_task", structuring_test_case_node)
    workflow.add_node("create_code_task", create_test_code_node)
    workflow.add_node("get_selector_task", get_selectors_node)
    workflow.add_node("save_task", save_node)

    # 任务
    workflow.add_edge(START, "structure_task")
    workflow.add_edge("structure_task", "get_selector_task")
    workflow.add_edge("get_selector_task", "create_code_task")
    workflow.add_edge("create_code_task", "save_task")
    workflow.add_edge("save_task", END)

    # 编译图
    graph = workflow.compile()

    # 打印图结构
    print("图结构:")
    print(graph.get_graph().draw_mermaid())

    return graph


def run_graph(test_case, url):
    print("=" * 50)
    print("LangGraph并行执行开始")
    print("=" * 50)
    # 创建初始状态
    initial_state = GenTestCodeState(
        url=url,
        test_type="ui",
        test_case=test_case,
        structured_test_case="",
        page_selector="",
        test_code=""
    )
    graph = create_graph()
    print("\n开始执行工作流...")
    print("-" * 50)
    final_state = graph.invoke(initial_state)
    print(final_state)
    print(final_state["test_case"])

    