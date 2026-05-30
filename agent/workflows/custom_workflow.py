from agent.utils.logger import get_logger

logger = get_logger(__name__)


class CustomWorkflow:
    def __init__(self, agent):
        self.agent = agent
        self.steps = []

    def add_step(self, tool: str, params: dict = None, description: str = ""):
        self.steps.append({"tool": tool, "params": params or {}, "description": description})
        return self

    def add_llm_step(self, prompt: str):
        self.steps.append({"type": "llm", "prompt": prompt, "description": "LLM processing step"})
        return self

    def add_conditional(self, condition_func, true_steps: list, false_steps: list):
        self.steps.append({
            "type": "conditional",
            "condition": condition_func,
            "true": true_steps,
            "false": false_steps,
        })
        return self

    async def execute(self, initial_input: str = None) -> str:
        logger.info(f"Custom workflow executing {len(self.steps)} steps")
        context = initial_input or ""
        for step in self.steps:
            if step.get("type") == "llm":
                result = await self.agent.llm.generate(step["prompt"].format(context=context))
            elif step.get("type") == "conditional":
                branch = step["true"] if step["condition"](context) else step["false"]
                for s in branch:
                    result = await self.agent.executor.execute_tool(s["tool"], s.get("params", {}))
            else:
                result = await self.agent.executor.execute_tool(step["tool"], step.get("params", {}))
            context += f"\n{result}"
        return context
