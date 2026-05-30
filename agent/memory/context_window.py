class ContextWindow:
    def __init__(self, max_tokens: int = 8000):
        self.max_tokens = max_tokens
        self._tokens = []

    def add(self, content: str, token_count: int = None):
        if token_count is None:
            token_count = len(content) // 4
        self._tokens.append({"content": content, "count": token_count})
        self._trim()

    def _trim(self):
        total = sum(t["count"] for t in self._tokens)
        while total > self.max_tokens and self._tokens:
            removed = self._tokens.pop(0)
            total -= removed["count"]

    def get_content(self) -> str:
        return "\n".join(t["content"] for t in self._tokens)

    def get_usage(self) -> dict:
        total = sum(t["count"] for t in self._tokens)
        return {"used": total, "max": self.max_tokens, "percent": (total / self.max_tokens) * 100}

    def clear(self):
        self._tokens.clear()
