from datetime import datetime
from typing import TypedDict, Dict, Any
from gen_test_report_agent.diagnose import diagnose
from langgraph.graph import START, END, StateGraph


class ReportState(TypedDict):
    feature_id: str
    report_file_path: str
    result: Dict[str, Any]


def test_report_create_node(state: ReportState):
    """提取测试报告信息"""
    print("生成测试报告信息")
    result = diagnose("./output/reporters/report.json")
    print(result)
    return {"result": result}


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(ReportState)

    # 添加节点
    workflow.add_node("test_report_create_task", test_report_create_node)

    # 任务
    workflow.add_edge(START, "test_report_create_task")
    workflow.add_edge("test_report_create_task", END)

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
        "report_file_path": "./output/codes/"
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
