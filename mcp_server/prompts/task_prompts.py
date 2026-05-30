TASK_RESEARCH = """Research the following topic thoroughly:
{topic}

Steps:
1. Search the web for information
2. Scrape relevant pages for detailed content
3. Compile findings with sources
4. Provide a comprehensive summary"""

TASK_ANALYSIS = """Analyze the following data:
{data}

Steps:
1. Understand the data structure
2. Perform calculations and transformations
3. Identify patterns and insights
4. Present findings clearly"""

TASK_CODE = """Write code to accomplish the following:
{requirement}

Steps:
1. Understand the requirements
2. Write the code
3. Test the code
4. Fix any issues"""


def get_task_prompt(task_type: str, **kwargs) -> str:
    prompts = {
        "research": TASK_RESEARCH,
        "analysis": TASK_ANALYSIS,
        "code": TASK_CODE,
    }
    template = prompts.get(task_type, "Complete the following task: {task}")
    return template.format(**kwargs)
