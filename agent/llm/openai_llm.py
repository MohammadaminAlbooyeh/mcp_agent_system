import os
import httpx
from openai import AsyncOpenAI


class OpenAILLM:
    def __init__(self, config: dict = None):
        self.config = config or {}
        api_key = os.getenv("OPENAI_API_KEY")
        try:
            self.client = AsyncOpenAI(api_key=api_key)
        except TypeError:
            # Fallback for version compatibility issues with httpx
            http_client = httpx.AsyncClient()
            self.client = AsyncOpenAI(api_key=api_key, http_client=http_client)
        self.model = self.config.get("model", "gpt-4")
        self.temperature = self.config.get("temperature", 0.7)

    async def generate(self, prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
        )
        return response.choices[0].message.content

    async def generate_with_system(self, system_prompt: str, user_prompt: str) -> str:
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=self.temperature,
        )
        return response.choices[0].message.content
