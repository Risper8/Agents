import asyncio
from typing import Optional
from src.modules.config_manager import ConfigManager
from src.modules.logging_setup import setup_logger

class BaseAgent:
    def __init__(self, config: ConfigManager):
        self.config = config
        self.logger = setup_logger(self.__class__.__name__)

    async def run(self):
        print(f"{self.config.AGENT_NAME} initialized. Type 'exit' to quit.")

        while True:
            user_input = await self.get_user_input()
            if user_input.lower() == 'exit':
                break

            response = await self.process_input(user_input)
            print(f"{self.config.AGENT_NAME}: {response}")

        print(f"{self.config.AGENT_NAME} shutting down. Goodbye!")

    async def get_user_input(self, prompt: Optional[str] = None) -> str:
        if prompt:
            print(prompt)
        user_input = await asyncio.get_event_loop().run_in_executor(None, input, f"{self.config.USER_NAME}> ")
        return user_input

    async def process_input(self, user_input: str) -> str:
        raise NotImplementedError("Subclasses must implement process_input method")

    async def add_to_history(self, user_input: str, response: str):
        # Implement this method to add the interaction to your chat history
        pass
