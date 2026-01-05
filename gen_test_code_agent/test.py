

import json

import sys
import os

# 获取当前文件的目录
current_dir = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录（假设项目根目录是 gen_test_case_agent 的父目录）
project_root = os.path.dirname(current_dir)
# 将项目根目录添加到 Python 路径
sys.path.insert(0, project_root)
from gen_test_code_agent.agent import run_graph
if __name__ == '__main__':
    ui_test_case = {
        "case_id": "TC-F_4aa9ded3-001",
        "feature_id": "F_4aa9ded3",
        "title": "用户登录-主流程-成功登录",
        "type": "main_flow",
        "preconditions": "用户拥有有效的手机号和密码",
        "steps": [
            "访问登录页面",
            "输入11位手机号",
            "输入至少8位且包含数字与字母的密码",
            "提交登录请求"
        ],
        "inputs": {
            "phone": "13800138000",
            "password": "pass1234"
        },
        "expected_results": "系统验证成功并返回token",
        "priority": "P0"
    }
    run_graph(json.dumps(ui_test_case), "http://localhost:5173/login")
