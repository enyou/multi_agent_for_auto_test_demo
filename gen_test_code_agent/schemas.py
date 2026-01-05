from enum import Enum
from typing import List
from pydantic import BaseModel, Field

class ActionEnum(str, Enum):
    GOTO = "goto"
    INPUT = "input"
    CLICK = "click"
    SELECT = "select"
    UPLOAD = "upload"
    WAIT = "wait"

class Step(BaseModel):
    action : ActionEnum = Field(description="动作")
    target: str= Field(description="操作的控件")
    value: str= Field(default="", description="赋予该控件的值")

class AssertionTypeEnum(str, Enum):
    PAGE = "page"
    ELEMENT = "element"
    BUSINESS = "business"

class Assertion(BaseModel):
    type: AssertionTypeEnum = Field(description="断言的类型")
    expected:str = Field(description="期待的内容")
    
class Priority(str, Enum):
    LOW = "P0"
    MEDIUM = "P2"
    HIGH = "P2"

class UITestCaseSchema(BaseModel):
    case_id: str = Field(description="测试CaseID")
    feature_id: str = Field(description="所属功能点ID")
    feature: str = Field(description="所属功能点名称")
    title: str = Field(description="测试用例标题")
    page: str = Field(description="UI测试的页面名称")
    preconditions: List[str] = Field(description="前置条件")
    steps: List[Step] = Field(description="测试步骤")
    assertions:  Assertion= Field(description="输出的结果判断的断言")
    priority: Priority = Field(description="优先级")