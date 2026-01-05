#-*- coding: utf-8 -*-
import json

import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（假设项目根目录是 gen_test_case_agent 的父目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 Python 路径
sys.path.insert(0, project_root)
from gen_test_case_agent.agent import run_graph

trm_text = {
    "features": [
        {
            "id": "F_4a300b9d",
            "name": "用户登录",
            "description": "用户通过手机号和密码进行登录验证，成功则返回访问令牌。"
        }
    ],
    "flows": [
        {
            "feature_id": "F_4a300b9d",
            "flow_id": "FLOW_d2fa6737",
            "name": "用户登录流程",
            "steps": [
                "输入手机号和密码",
                "系统验证手机号格式（11位数字）",
                "系统验证密码格式（至少8位，包含数字与字母）",
                "系统检查密码错误次数是否超过5次（若超过则锁定账号10分钟）",
                "发送POST请求到/api/login接口",
                "接收响应（成功返回token，失败返回错误信息）"
            ]
        }
    ],
    "api": [
        {
            "method": "POST",
            "url": "/api/login",
            "name": "用户登录功能",
            "description": "用户可以在登录页面输入手机号与密码进行登录。\n- 手机号必须为 11 位数字。\n- 密码需至少 8 位，并且包含数字与字母。\n- 若密码错误次数超过 5 次，则账号锁定 10 分钟。",
            "request_params": [
                {
                    "param": "phone",
                    "param_type": "string",
                    "description": "手机号"
                },
                {
                    "param": "password",
                    "param_type": "string",
                    "description": "登录密码"
                }
            ],
            "response_examples": ['{\n  "code": 0,\n  "msg": "ok",\n  "data": {"token": "xxxxx"}\n}',
                                  '{\n  "code": 401,\n  "msg": "Unauthorized"\n}'],
            "feature_id": "F_4a300b9d"
        }
    ],
    "rules": [
        {
            "feature_id": "F_4a300b9d",
            "rule_id": "R_4545be02",
            "text": "手机号必须为 11 位数字。",
            "type": "input_validation",
            "normalized": "手机号长度必须为11位，且仅包含数字。"
        },
        {
            "feature_id": "F_4a300b9d",
            "rule_id": "R_fa199191",
            "text": "密码需至少 8 位，并且包含数字与字母。",
            "type": "input_validation",
            "normalized": "密码长度至少为8位，且必须同时包含数字和字母。"
        },
        {
            "feature_id": "F_4a300b9d",
            "rule_id": "R_ed42c16d",
            "text": "若密码错误次数超过 5 次，则账号锁定 10 分钟。",
            "type": "rate_limit",
            "normalized": "连续登录失败次数达到5次后，账号将被锁定10分钟。"
        },
        {
            "feature_id": "F_4a300b9d",
            "rule_id": "R_12d058ad",
            "text": "POST /api/login",
            "type": "auth",
            "normalized": "登录接口的请求方法为POST，路径为/api/login。"
        }
    ],
    "exceptions": []
}


run_graph(json.dumps(trm_text))
