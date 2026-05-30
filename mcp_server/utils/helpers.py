import json
import hashlib
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    hash_input = f"{timestamp}{__import__('random').random()}"
    short_hash = hashlib.md5(hash_input.encode()).hexdigest()[:8]
    return f"{prefix}{timestamp}_{short_hash}" if prefix else f"{timestamp}_{short_hash}"


def truncate_text(text: str, max_length: int = 1000) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def safe_json_loads(data: str) -> dict:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}


def format_size(size_bytes: int) -> str:
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"
