import asyncio
from mcp_server.tools.utility_tools.calculator import CalculatorTool
from mcp_server.tools.utility_tools.datetime_tool import DateTimeTool


async def main():
    calc = CalculatorTool()
    result = await calc.execute(expression="2 + 3 * 4")
    print(f"Calculator: {result}")

    dt = DateTimeTool()
    now = await dt.execute(operation="now")
    print(f"Current time: {now}")


if __name__ == "__main__":
    asyncio.run(main())
