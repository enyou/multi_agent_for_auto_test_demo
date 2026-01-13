import json
import hashlib
from datetime import datetime


# ---------- 工具方法 ----------

def stack_hash(traceback: str) -> str:
    """用 traceback 生成稳定 hash，用于影响范围判断"""
    if not traceback:
        return ""
    return hashlib.md5(traceback.encode("utf-8")).hexdigest()[:8]


def classify_failure(error_type: str, error_message: str) -> str:
    """MVP 失败分类规则"""
    if not error_type:
        return "UNKNOWN"

    if "Connection" in error_type:
        return "ENVIRONMENT"
    if "Timeout" in error_type:
        return "TIMEOUT"
    if "NoSuchElement" in error_message:
        return "UI_CHANGE"
    if "AssertionError" in error_type:
        return "ASSERTION"

    return "UNKNOWN"


def is_flaky(pass_rate: float) -> bool:
    """MVP flaky 判断"""
    return pass_rate < 0.95


# ---------- 历史数据（MVP 用 mock） ----------

MOCK_HISTORY = {
    "tests/test_login.py::test_login_fail": {
        "pass_rate": 0.72,
        "last_outcome": "passed"
    }
}


# ---------- 诊断主逻辑 ----------

def diagnose(report_path: str):
    with open(report_path, "r", encoding="utf-8") as f:
        report = json.load(f)

    tests = report.get("tests", [])
    diagnostics = []

    # 先算 stack_hash 的影响范围
    stack_counter = {}

    for test in tests:
        call = test.get("call", {})
        crash = call.get("crash", {})
        tb = crash.get("traceback", "")
        h = stack_hash(tb)
        if h:
            stack_counter[h] = stack_counter.get(h, 0) + 1

    # 单条用例诊断
    for test in tests:
        nodeid = test["nodeid"]
        outcome = test["outcome"]

        history = MOCK_HISTORY.get(nodeid, {})
        last_outcome = history.get("last_outcome")
        pass_rate = history.get("pass_rate", 1.0)

        diagnosis = {
            "nodeid": nodeid,
            "outcome": outcome,
            "timestamp": datetime.utcnow().isoformat(),
            "diagnosis": {}
        }

        if outcome == "failed":
            crash = test.get("call", {}).get("crash", {})
            error_type = crash.get("message", "")
            traceback = crash.get("traceback", "")

            failure_type = classify_failure(error_type, traceback)
            flaky = is_flaky(pass_rate)
            regression = last_outcome == "passed"

            h = stack_hash(traceback)
            impact = stack_counter.get(h, 1)

            diagnosis["diagnosis"] = {
                "category": failure_type,
                "regression": regression,
                "flaky": flaky,
                "impact": impact,
                "suggestion": build_suggestion(
                    failure_type, flaky, regression
                )
            }

        diagnostics.append(diagnosis)

    return diagnostics


def build_suggestion(category, flaky, regression):
    if flaky:
        return "用例不稳定，建议重跑或隔离"
    if category == "ENVIRONMENT":
        return "检查环境或依赖服务"
    if regression:
        return "疑似新引入问题，优先排查最近变更"
    if category == "ASSERTION":
        return "业务断言失败，检查系统逻辑"
    return "需要人工分析"
