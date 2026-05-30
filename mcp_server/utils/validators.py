import re
from urllib.parse import urlparse


def validate_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def validate_sql_query(query: str) -> bool:
    forbidden = ["DROP", "TRUNCATE", "ALTER", "CREATE"]
    upper = query.strip().upper()
    for keyword in forbidden:
        if upper.startswith(keyword):
            return False
    return True


def validate_file_path(path: str) -> bool:
    import os
    if ".." in path:
        return False
    return True
