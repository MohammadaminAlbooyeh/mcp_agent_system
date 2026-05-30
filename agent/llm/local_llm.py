import httpx


class LocalLLM:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.base_url = self.config.get("base_url", "http://localhost:11434")
        self.model = self.config.get("model", "llama2")
        self.client = httpx.AsyncClient(base_url=self.base_url)

    async def generate(self, prompt: str) -> str:
        response = await self.client.post(
            "/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
        )
        data = response.json()
        return data.get("response", "")

    async def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        full_prompt = f"{system_prompt}\n\n{user_prompt}"
        return await self.generate(full_prompt)
