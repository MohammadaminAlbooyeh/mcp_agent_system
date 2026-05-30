import json
import os


class LongTermMemory:
    def __init__(self, storage_path: str = "memory_store.json"):
        self.storage_path = storage_path
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {}

    def _save(self):
        with open(self.storage_path, "w") as f:
            json.dump(self._data, f, indent=2)

    def store(self, key: str, value: any):
        self._data[key] = value
        self._save()

    def retrieve(self, key: str) -> any:
        return self._data.get(key)

    def search(self, query: str) -> list[tuple[str, any]]:
        results = []
        for key, value in self._data.items():
            if query.lower() in key.lower():
                results.append((key, value))
        return results

    def clear(self):
        self._data.clear()
        self._save()
