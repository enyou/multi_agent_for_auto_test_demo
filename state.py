from typing_extensions import Annotated, TypedDict, List, Dict, Optional, Any

from utils.tools import append_reducer


class AgentStatus(TypedDict):
    """Agent Status"""
    document_parser:str
    test_case_generator: str
    test_code_generator: str
    code_executor: str
    report_agent: str


class Requirement(TypedDict):
    """
     需求文档解析agent状态
    """
    feature: str
    ext_features: Dict[str, str]
    ext_apis: Annotated[List[Any], append_reducer]
    ext_flows: Annotated[List[Any], append_reducer]
    ext_rules: Annotated[List[Any], append_reducer]
    ext_exceptions: Annotated[List[Any], append_reducer]


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

class TestCode(TypedDict):
    """
        测试代码生成的agent状态
    """
    case_id: str
    test_code: str
    code_name: str

class ExecutionResult(TypedDict):
    """
        执行结果Agent状态
    """
    case_id: str
    exe_result: str
    failed_reasons: str
    failed_logs: str


class Bug(TypedDict):
    """bug票Agent状态"""
    title: str
    cases: List[str]


# ===============================
# 2. Router State 类型定义
# {
#     "session_id": "S-001",
#     "intent": "auto_test_from_prd",
#     "current_stage": "execution_done",
#     "workflow_status": "running",
#     "agent_status": {
#         "document_parser": "done",
#         "test_case_generator": "done",
#         "test_code_generator": "done",
#         "code_executor": "done",
#         "report_agent": "pending"
#     },
#     "decisions": {
#         "need_bug_ticket": true
#     },
#     "retry_info": {
#         "test_code_generator": 0,
#         "code_executor": 1
#     }
# }
# ===============================

class RouterState(TypedDict):
    """
    RouterState 的状态
    """
    session_id: str
    current_stage: str
    workflow_status: str
    agent_status:  Optional[AgentStatus]
    decisions: Dict[str, bool]
    retry_info: Dict[str, int]

# ===============================
# 2. Shared State 类型定义
# {
#         "session_id": "S-001",
#         "requirements": {
#             "feature": "login",
#             "scenarios": ["valid", "invalid"]
#         },
#         "test_cases": [
#             {
#             "id": "TC-01",
#             "steps": ["input user", "input pwd"]
#             }
#         ],
#         "test_code": [],
#         "execution_result": {
#             "passed": 8,
#             "failed": 2,
#             "failed_cases": ["TC-03"]
#         },
#         "report": null,
#         "bugs": []
# }
# ===============================
class GlobalState(TypedDict):
    """
        global state 
    """
    # ===== Shared State（数据面）=====
    feature_id: str
    fragment:str
    requirements: Optional[Requirement]
    trm_result: Optional[Dict[str, Any]]
    test_cases: Optional[List[TestCase]]
    test_code: Optional[List[TestCode]]
    execution_result: Optional[List[ExecutionResult]]
    report: Optional[Dict[str, Any]]
    bugs: Optional[List[Bug]]

    # ===== Router State（控制面）=====
    router: RouterState