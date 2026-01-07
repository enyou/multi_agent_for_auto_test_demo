from typing_extensions import List
from enum import Enum
from pydantic import BaseModel, Field


class RuleType(str, Enum):

    INPUT_VALIDATION = "input_validation"
    RATE_LIMIT = "rate_limit"
    AUTH = "auth"
    OTHER = "other"


class FeatureSchema(BaseModel):
    feature: str = Field(description="Feature的名称")
    description: str = Field(description="Feature描述")
    inputs: List[str] = Field(description="输入参数")
    outputs: List[str] = Field(description="输出参数")
    rules: List[str] = Field(description="规则列表")
    exceptions: List[str] = Field(description="异常列表")


class ApiRequestParamsSchema(BaseModel):
    param: str = Field(description="输入的参数")
    param_type: str = Field(description="输入的参数类型")
    description: str = Field(description="输入的参数描述")


class ApiSchema(BaseModel):

    method: str = Field(description="HTTP 方法")
    url: str = Field(description="API URL")
    name: str = Field(description="API 名称")
    description: str = Field(description="API 说明")
    request_params: List[ApiRequestParamsSchema] = Field(description="请求参数")
    response_examples: List[str] = Field(description="响应示例")


class FlowSchema(BaseModel):

    name: str = Field(description="Feature的名称")
    steps: List[str] = Field(description="步骤列表")


class RuleSchema(BaseModel):
    text: str = Field(description="规则的原始文本"),
    type: RuleType = Field(description="类型", examples=[
                      "input_validation", "rate_limit", "auth", "other"])
    normalized: str = Field(description="规范化文本")
