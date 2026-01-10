from langgraph.graph import START, END, StateGraph
from state import GlobalState
from gen_test_case_agent.agent import create_graph as test_case_create_agent
from gen_test_code_agent.agent import create_graph as test_code_create_agent
from requirement_analyzer_agent.agent import create_graph as trm_create_agent


def trm_create_node(state: GlobalState):
    """需求解析节点"""
    result = trm_create_agent().invoke({"feature_id": state["feature_id"],
                                        "fragment": state["fragment"]})
    return {"doc_parser_result": result}


def test_case_create_node(state: GlobalState):
    """生成测试用例节点"""
    return test_case_create_agent().invoke(state)


def test_code_create_node(state: GlobalState):
    """生成代码节点"""
    return test_code_create_agent().invoke(state)


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(GlobalState)

    # 添加节点
    workflow.add_node("create_trm_task", trm_create_node)
    workflow.add_node("create_test_case_task", test_case_create_node)
    workflow.add_node("create_test_code_task", test_code_create_node)

    # 任务
    workflow.add_edge(START, "create_trm_task")
    workflow.add_edge("create_trm_task", "create_test_case_task")
    workflow.add_edge("create_test_case_task", "create_test_code_task")
    workflow.add_edge("create_test_case_task", END)

    # 编译图
    graph = workflow.compile()

    return graph


def run(user_input: str):
    """
    执行工作流
    """
    print("=" * 50)

    # 创建初始状态
    initial_state = {
        "feature_id": "123",
        "fragment": user_input,
        "requirements": {},
        "test_cases": None,
        "test_code": None,
        "execution_result": None,
        "report": None,
        "bugs": [],
        "router": {
            "session": "123",
            "current_stage": "init",
            "workflow_status": "running",
            "agent_status": None,
            "decisions": None,
            "retry_info": None
        }
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


if __name__ == "__main__":
    SAMPLE_MD = """
            # 登录与用户管理模块需求说明

            ## 1. 用户登录功能
            用户可以在登录页面输入手机号与密码进行登录。
            - 手机号必须为 11 位数字。
            - 密码需至少 8 位，并且包含数字与字母。
            - 若密码错误次数超过 5 次，则账号锁定 10 分钟。

            请求方式：
            POST /api/login

            请求参数：
            | 参数 | 类型 | 说明 |
            |------|------|------|
            | phone | string | 手机号 |
            | password | string | 登录密码 |

            响应示例（成功）：
            {
            "code": 0,
            "msg": "ok",
            "data": { "token": "xxxxx" }
            }

            响应示例（失败）：
            {
            "code": 401,
            "msg": "Unauthorized"
            }
    """
    run(SAMPLE_MD)
