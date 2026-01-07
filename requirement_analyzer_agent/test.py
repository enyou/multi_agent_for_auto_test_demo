from requirement_analyzer_agent.agent import run_graph
if __name__ == '__main__':
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
    run_graph(SAMPLE_MD)
