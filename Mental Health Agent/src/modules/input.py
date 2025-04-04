import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from config import USER_NAME
from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from src.modules.logging_setup import logger

def get_user_input():
    prompt = f"{USER_NAME}> \n"
    history_file = os.path.expanduser("~/.input_history")

    kb = KeyBindings()

    @kb.add('c-c')
    @kb.add('c-d')
    def _(event):
        " Pressing Ctrl-C or Ctrl-D will exit the user interface. "
        event.app.exit()

    # Define the style for the prompt
    style = Style.from_dict({
        'prompt': 'ansigreen bold',
    })

    session = PromptSession(
        history=FileHistory(history_file),
        auto_suggest=AutoSuggestFromHistory(),
        complete_while_typing=True,
        enable_history_search=True,
        vi_mode=True,
        key_bindings=kb,
        style=style,
        message=[('class:prompt', prompt)]
    )

    try:
        user_input = session.prompt()
        logger.debug(f"User input received: {user_input[:50]}...")  # Log only first 50 characters
        return user_input
    except KeyboardInterrupt:
        logger.info("Input interrupted by user (KeyboardInterrupt)")
        print("\nOperation cancelled by user.")
        return None
    except EOFError:
        logger.info("EOF detected, exiting program")
        print("\nEOF detected. Exiting program.")
        return None

# # Example usage
# if __name__ == "__main__":
#     logger.info("Input module test started")
#     print("Enter your input below.")
#     while True:
#         result = get_user_input()
#         if result is None:
#             logger.info("Input module test ended")
#             break
#         print(f"You entered: {result}")
#     logger.info("Input module test completed")
