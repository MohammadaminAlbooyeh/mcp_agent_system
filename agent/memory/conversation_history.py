class ConversationHistory:
    def __init__(self, max_length: int = 100):
        self.max_length = max_length
        self._history = []

    def add(self, message: dict):
        self._history.append(message)
        if len(self._history) > self.max_length:
            self._history.pop(0)

    def get_all(self) -> list[dict]:
        return list(self._history)

    def get_recent(self, n: int = 10) -> list[dict]:
        return self._history[-n:]

    def clear(self):
        self._history.clear()

    def __len__(self) -> int:
        return len(self._history)
