# app/utils/llm_client.py
import os
import traceback
from langchain_openai.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.llm import LLMChain
from langchain_core.output_parsers import JsonOutputParser
from dotenv import load_dotenv
load_dotenv()


class LLMClient:

    def __init__(self, model_name: str = None, base_url: str = None, temperature: float = 0.0):
        model_name = model_name or os.environ.get("OPENAI_MODEL_NAME")
        base_url = os.environ.get("OPENAI_API_URL")
        self.temperature = temperature
        self.client = ChatOpenAI(
            model_name=model_name, base_url=base_url, temperature=temperature, streaming=True)

    def run_prompt(self, system_prompt: str, user_prompt: str, input: dict, parser: JsonOutputParser = None) -> str:
        """
        Run a structured prompt using LangChain LLMChain and PromptTemplate.
        Returns raw text.
        """
        try:
            prompt = ChatPromptTemplate.from_messages(
                [system_prompt, user_prompt]
            )
            if parser:
                prompt = prompt.partial(
                    format_instructions=parser.get_format_instructions())
                chain = prompt | self.client | parser
            else:
                chain = prompt | self.client
            resp = chain.invoke(input=input)
            return resp
        except Exception as e:
            print(traceback.format_exc())
            print("LLM call failed: %s", e)
            raise


llm_client = LLMClient()

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
    import sys
    llm_client = LLMClient()
    sys.path.append(os.path.dirname(
        os.path.dirname(os.path.abspath(__file__))))
    from requirement_analyzer_agent.prompts import ExtractFeaturePrompt, CommonUserPrompt
    from requirement_analyzer_agent.schemas import FeatureSchema
    parser = JsonOutputParser(pydantic_object=FeatureSchema)
    import os
    resp = llm_client.run_prompt(system_prompt=ExtractFeaturePrompt.system_prompt,
                                 user_prompt=CommonUserPrompt.prompt,
                                 input={"fragment": SAMPLE_MD},
                                 parser=parser)
    print(resp)
