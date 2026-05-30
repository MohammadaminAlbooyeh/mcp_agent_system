from mcp_server.utils.logger import get_logger

logger = get_logger(__name__)


class PromptHandler:
    def __init__(self, server):
        self.server = server

    async def handle_prompt_request(self, prompt_type: str, **kwargs) -> str:
        try:
            from mcp_server.prompts.system_prompts import get_system_prompt
            from mcp_server.prompts.task_prompts import get_task_prompt
            from mcp_server.prompts.agent_prompts import get_agent_prompt

            if prompt_type == "system":
                return get_system_prompt(**kwargs)
            elif prompt_type == "task":
                return get_task_prompt(**kwargs)
            elif prompt_type == "agent":
                return get_agent_prompt(**kwargs)
            else:
                return f"Unknown prompt type: {prompt_type}"
        except Exception as e:
            logger.error(f"Error getting prompt {prompt_type}: {e}")
            return f"Error: {e}"
