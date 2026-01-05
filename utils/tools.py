import uuid


def make_id(prefix: str):
    return f"{prefix}_{uuid.uuid4().hex[:8]}"