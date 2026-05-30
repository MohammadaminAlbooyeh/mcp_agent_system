class ShortTermMemory:
    def __init__(self):
        self._data = {}

    def store(self, key: str, value: any):
        self._data[key] = value

    def retrieve(self, key: str) -> any:
        return self._data.get(key)

    def get_all(self) -> dict:
        return dict(self._data)

    def clear(self):
        self._data.clear()

    def remove(self, key: str):
        self._data.pop(key, None)
