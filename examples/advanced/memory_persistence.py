import asyncio
from agent.memory.memory_manager import MemoryManager


async def main():
    mm = MemoryManager()
    mm.store("user_preference", "dark_mode", memory_type="long_term")
    retrieved = mm.retrieve("user_preference", memory_type="long_term")
    print(f"Retrieved preference: {retrieved}")

    results = mm.long_term.search("preference")
    print(f"Search results: {results}")


if __name__ == "__main__":
    asyncio.run(main())
