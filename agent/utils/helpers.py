import json
import time


def timer(func):
    async def wrapper(*args, **kwargs):
        start = time.time()
        result = await func(*args, **kwargs)
        elapsed = time.time() - start
        return {"result": result, "elapsed": elapsed}
    return wrapper


def format_tool_result(result: str, max_length: int = 500) -> str:
    if len(result) > max_length:
        return result[:max_length] + "..."
    return result


def merge_dicts(*dicts: dict) -> dict:
    result = {}
    for d in dicts:
        result.update(d)
    return result


def safe_get(data: dict, *keys, default=None):
    for key in keys:
        try:
            data = data[key]
        except (KeyError, TypeError, IndexError):
            return default
    return data
