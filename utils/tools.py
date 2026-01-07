import uuid
from typing import List, Any


def make_id(prefix: str):
    """create id"""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def append_reducer(old_list: List[Any], new_items: Any) -> List[Any]:
    """list 方法"""
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