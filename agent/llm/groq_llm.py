import os
from groq import AsyncGroq


class GroqLLM:
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = self.config.get("model", "mixtral-8x7b-32768")
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
