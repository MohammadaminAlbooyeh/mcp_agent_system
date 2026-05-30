AGENT_REACT_PROMPT = """You are an AI agent that follows the ReAct (Reasoning + Acting) pattern.

For each step, follow this format:

Thought: Consider what you need to do and which tool to use
Action: The tool you want to call
Action Input: Parameters for the tool
Observation: The result from the tool

After gathering enough information, provide:
Final Answer: Your complete response to the user

Available tools:
{tools}

Remember:
1. Think step by step
2. Use one tool at a time
3. Observe the result before proceeding
4. Stop when you have enough information"""

AGENT_PLANNER_PROMPT = """Create a step-by-step plan to accomplish the following task:

Task: {task}

Available tools:
{tools}

Format your plan as:
Step 1: [description] -> Tool: [tool_name]
Step 2: [description] -> Tool: [tool_name]
...
"""

AGENT_REFLECTION_PROMPT = """Review the following execution and identify if the result is satisfactory:

Task: {task}
Steps Taken: {steps}
Results: {results}

Evaluate:
1. Was the task completed successfully?
2. Are the results accurate and complete?
3. Should any steps be retried or corrected?
4. What improvements could be made?"""


def get_agent_prompt(prompt_type: str, **kwargs) -> str:
    prompts = {
        "react": AGENT_REACT_PROMPT,
        "planner": AGENT_PLANNER_PROMPT,
        "reflection": AGENT_REFLECTION_PROMPT,
    }
    template = prompts.get(prompt_type, "{task}")
    return template.format(**kwargs)
