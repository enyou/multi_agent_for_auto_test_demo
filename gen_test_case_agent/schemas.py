from enum import Enum
from typing_extensions import List
from pydantic import BaseModel, Field


class TestCaseType(str, Enum):
    MAIN_FLOW = "main_flow"
    SUB_FLOW = "sub_flow"
    RULE_BOUNDARY = "rule_boundary"
    RULE_EQUIVALENCE = "rule_equivalence"
    API_VALIDATION = "api_validation"
    EXCEPTION = "exception"
    SCENARIO = "scenario"


class Priority(str, Enum):
    LOW = "P0"
    MEDIUM = "P2"
    HIGH = "P2"


class TestSchema(BaseModel):
    feature_id: str = Field(description="所属功能点ID")
    feature: str = Field(description="所属功能点名称")
    title: str = Field(description="测试用例标题")
    type: TestCaseType = Field(description="用例类型")
    preconditions: str = Field(default="", description="前置条件")
    steps: List[str] = Field(description="测试步骤")
    inputs: dict = Field(description="输入数据")
    expected_results: str = Field(description="预期结果")
    priority: Priority = Field(description="优先级")
