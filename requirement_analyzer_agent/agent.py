import json
from typing import Any, List, TypedDict
from langgraph.graph import StateGraph, END, START
from langchain_core.output_parsers import JsonOutputParser
from utils.llm_client import llm_client
import requirement_analyzer_agent.schemas as schema
from requirement_analyzer_agent.prompts import *
from typing import Annotated
from utils.tools import make_id


def append_reducer(old_list: List[Any], new_items: Any) -> List[Any]:
    """将新内容追加到列表的合并函数"""
    if old_list is None:
        old_list = []
    if new_items is None:
        return old_list
    # 如果新内容本身是列表，则扩展
    if isinstance(new_items, list):
        if old_list:
            return old_list + new_items
        return new_items
    # 否则作为单个元素追加
    if old_list:
        return old_list + [new_items]
    return [new_items]


class TRMState(TypedDict):
    requirement_text: str
    ext_features: Annotated[List[Any], append_reducer]
    ext_apis: Annotated[List[Any], append_reducer]
    ext_flows: Annotated[List[Any], append_reducer]
    ext_rules: Annotated[List[Any], append_reducer]
    ext_exceptions: Annotated[List[Any], append_reducer]
    feature_id: str
    trm_result: dict


def extract_feature_node(state: TRMState):
    input = state["requirement_text"]
    parser = JsonOutputParser(pydantic_object=schema.FeatureSchema)
    resp = llm_client.run_prompt(system_prompt=ExtractFeaturePrompt.system_prompt,
                                 user_prompt=CommonUserPrompt.prompt,
                                 input={"fragment": input},
                                 parser=parser)
    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)
    return {"ext_features": result}


def extract_api_node(state: TRMState) -> TRMState:
    input = state["requirement_text"]
    parser = JsonOutputParser(pydantic_object=schema.ApiSchema)
    resp = llm_client.run_prompt(system_prompt=ExtractApiPrompt.system_prompt,
                                 user_prompt=CommonUserPrompt.prompt,
                                 input={"fragment": input},
                                 parser=parser)
    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)

    return {"ext_apis": result}


def extract_flow_node(state: TRMState) -> TRMState:
    input = state["requirement_text"]
    parser = JsonOutputParser(pydantic_object=schema.FlowSchema)
    resp = llm_client.run_prompt(system_prompt=ExtractFlowPrompt.system_prompt,
                                 user_prompt=CommonUserPrompt.prompt,
                                 input={"fragment": input},
                                 parser=parser)

    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)
    return {"ext_flows": result}


def extract_rule_node(state: TRMState) -> TRMState:
    input = state["requirement_text"]
    parser = JsonOutputParser(pydantic_object=schema.RuleSchema)
    resp = llm_client.run_prompt(system_prompt=ExtractRulePrompt.system_prompt,
                                 user_prompt=CommonUserPrompt.prompt,
                                 input={"fragment": input},
                                 parser=parser)

    result = resp
    if isinstance(resp, str):
        result = json.loads(resp)
    return {"ext_rules": result}


def extract_exception_node(state: TRMState) -> TRMState:
    return state


def collect_result_node(state: TRMState) -> TRMState:
    """
    合并抽取的feature, api, flow, rule, exception信息, 生成TRM
    """
    print("start to collect")
    feature_id = state["feature_id"]
    features = state["ext_features"]
    flows = state["ext_flows"]
    rules = state["ext_rules"]
    apis = state["ext_apis"]
    feat_list = []
    for f in features:
        feat_list.append({"id": feature_id, "name": f.get("feature") or f.get(
            "name") or feature_id, "description": f.get("description", "")})

    flow_list = []
    for fl in flows:
        flow_list.append({"feature_id": feature_id, "flow_id": make_id(
            "FLOW"), "name": fl.get("name", "flow"), "steps": fl.get("steps", [])})

    api_list = []
    for a in apis:
        a_entry = a.copy()
        a_entry.setdefault("feature_id", feature_id)
        api_list.append(a_entry)

    rule_list = []
    for r in rules:
        rule_list.append({"feature_id": feature_id, "rule_id": make_id("R"), "text": r.get(
            "text"), "type": r.get("type", "input_validation"), "normalized": r.get("normalized", "")})

    return {"trm_result": {
        "features": feat_list,
        "flows": flow_list,
        "api": api_list,
        "rules": rule_list,
        "exceptions": []
    }}


def create_graph():
    """创建并运行简单的并行图"""
    print("开始创建图")
    # 创建图
    workflow = StateGraph(TRMState)

    # 添加节点
    workflow.add_node("ext_feature_task", extract_feature_node)
    workflow.add_node("ext_api_task", extract_api_node)
    workflow.add_node("ext_flow_task", extract_flow_node)
    workflow.add_node("ext_rule_task", extract_rule_node)
    workflow.add_node("ext_exception_task", extract_exception_node)
    workflow.add_node("collect_result_task", collect_result_node)

    # 并行任务
    workflow.add_edge(START, "ext_feature_task")
    workflow.add_edge(START, "ext_api_task")
    workflow.add_edge(START, "ext_flow_task")
    workflow.add_edge(START, "ext_rule_task")
    workflow.add_edge(START, "ext_exception_task")

    # 结果合并业务
    workflow.add_edge("ext_feature_task", "collect_result_task")
    workflow.add_edge("ext_api_task", "collect_result_task")
    workflow.add_edge("ext_flow_task", "collect_result_task")
    workflow.add_edge("ext_rule_task", "collect_result_task")
    workflow.add_edge("ext_exception_task", "collect_result_task")

    # 结束
    workflow.add_edge("collect_result_task", END)

    # 编译图
    graph = workflow.compile()

    # 打印图结构
    print("图结构:")
    print(graph.get_graph().draw_mermaid())

    return graph


def run_graph(input):
    print("=" * 50)
    print("LangGraph并行执行开始")
    print("=" * 50)
    # 创建初始状态
    initial_state = TRMState(
        requirement_text=input,
        ext_features=[],
        ext_apis=[],
        ext_flows=[],
        ext_rules=[],
        ext_exceptions=[],
        feature_id=make_id("F"),
        trm_result={}
    )
    graph = create_graph()
    print("\n开始执行工作流...")
    print("-" * 50)
    final_state = graph.invoke(initial_state)
    print(final_state["trm_result"])
