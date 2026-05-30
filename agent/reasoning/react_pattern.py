from agent.utils.logger import get_logger

logger = get_logger(__name__)


class ReActPattern:
    def __init__(self, agent):
        self.agent = agent
        self.max_iterations = 10

    async def run(self, task: str) -> str:
        context = f"Task: {task}"
        for i in range(self.max_iterations):
            thought = await self._think(context)
            if self._is_final(thought):
                return thought
            action, params = self._parse_action(thought)
            if not action:
                return thought
            observation = await self._act(action, params)
            context += f"\nThought: {thought}\nAction: {action}\nObservation: {observation}"
        return context

    async def _think(self, context: str) -> str:
        prompt = (
            f"{context}\n\n"
            "What should I do next? Respond with:\n"
            "Thought: [your reasoning]\n"
            "Action: [tool_name]\n"
            "Action Input: [params]\n"
            "or Final Answer: [response]"
        )
        return await self.agent.llm.generate(prompt)

    def _is_final(self, thought: str) -> bool:
        return "Final Answer:" in thought

    def _parse_action(self, thought: str) -> tuple[str, dict]:
        lines = thought.split("\n")
        action, params = None, {}
        for line in lines:
            if line.startswith("Action:"):
                action = line.split(":", 1)[1].strip()
            elif line.startswith("Action Input:"):
                import json
                try:
                    params = json.loads(line.split(":", 1)[1].strip())
                except json.JSONDecodeError:
                    params = {"input": line.split(":", 1)[1].strip()}
        return action, params

    async def _act(self, action: str, params: dict) -> str:
        try:
            return await self.agent.executor.execute_tool(action, params)
        except Exception as e:
            return f"Error: {e}"
