from datetime import datetime
from typing import TypedDict
from langgraph.graph import START, END, StateGraph
import pytest


class RunnerState(TypedDict):
    feature_id: str
    file_path: str
    output_path: str


def test_code_create_node(state: RunnerState):
    """测试代码执行节点"""
    print("执行代码")
    create_date = datetime.now().strftime("%Y%m%d%H%M%S")
    feature_id = state["feature_id"]
    reporter_file_name = f"./output/reporters/report_{feature_id}_{create_date}.json"
    pytest.main([
        state["file_path"],
        "--json-report",
        "--json-report-file={}".format(reporter_file_name)
    ])
    return state


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(RunnerState)

    # 添加节点
    workflow.add_node("run_test_code_task", test_code_create_node)

    # 任务
    workflow.add_edge(START, "run_test_code_task")
    workflow.add_edge("run_test_code_task", END)

    # 编译图
    graph = workflow.compile()

    return graph


def run():
    """
    执行工作流
    """
    print("=" * 50)

    # 创建初始状态
    initial_state = {
        "feature_id": "123",
        "file_path": "/Users/a1234/Documents/auto_test_by_ai/output/codes/"
    }
    print("--------------------初始化状态--------------")
    print(initial_state)
    print("-------------------------------------------")
    graph = create_graph()
    print("\n开始执行工作流...")
    print("-" * 50)
    final_state = graph.invoke(initial_state)
    print(final_state)
    print("-" * 50)
    print("工作流执行完毕")
