import json
import hashlib
from datetime import datetime


def generate_id(prefix: str = "") -> str:
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    short_hash = hashlib.md5(f"{timestamp}{__import__('random').random()}".encode()).hexdigest()[:8]
    return f"{prefix}{timestamp}_{short_hash}" if prefix else f"{timestamp}_{short_hash}"


def parse_json_safe(data: str) -> dict:
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError):
        return {}


def paginate(items: list, page: int = 1, per_page: int = 20) -> dict:
    start = (page - 1) * per_page
    end = start + per_page
    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "per_page": per_page,
        "total_pages": (len(items) + per_page - 1) // per_page,
    }
