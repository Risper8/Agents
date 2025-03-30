from src.modules.logging_setup import logger
from src.modules.errors import InputError, APIConnectionError
from src.modules.ollama_client import process_prompt
# from src.modules.input import get_user_input
from config import DEFAULT_MODEL, AGENT_NAME
from rich.prompt import Confirm, Prompt
from src.modules.save_history import chat_history
from src.modules.context_management import gather_context, adapt_context_to_user

class MentalHealthAgent:
    def __init__(self, model_name=DEFAULT_MODEL):
        self.model_name = model_name
        self.context = ""
        self.conversation_history = []

    def run_agent(self, user_message=None, user_id=None):
        logger.info(f"Starting {AGENT_NAME} Mental Health Agent")

        if not user_message:
            logger.warning("No user message received. Agent remains idle.")
            return "I'm here whenever you're ready to talk. 💙"

        if user_message == 'CONTINUE':
            return "Continuing our conversation, I'm here for you! 😊"
        
        if user_message.lower() == 'clear history':
            chat_history.clear()
            self.conversation_history.clear()
            logger.info("Conversation history and context cleared.")
            return "History Cleared 🧹"
 
        try:
            logger.info(f"User input: {user_message}")
            prompt = f"""
            You are a compassionate and empathetic AI assistant known as {AGENT_NAME}, designed to engage in thoughtful and supportive conversations every day.
            Respond kindly and supportively to: {user_message}.
            Your role is to offer friendly, non-judgmental support and be someone the user can talk to, no matter how they are feeling. 
            Focus on creating a space where the user feels comfortable sharing their thoughts, whether they're having a good day, a neutral day, or a bad day.
            Your responses should never assume that the user is in distress; instead, engage in a conversation with the goal of being present, listening, and offering support when necessary.
            You should ask open-ended questions and be empathetic without overloading the user with advice unless they ask for it.
            It's important to foster a positive, warm connection, and be ready to provide resources or suggestions if the user needs them.
            You are there to listen and provide comfort, no matter what the situation is.
            """
            self.context = gather_context(user_message, self.conversation_history, AGENT_NAME)
            self.context = adapt_context_to_user(self.context, self.model_name)
            response = process_prompt(prompt, self.model_name, "MentalHealthAgent", self.context)
            logger.info(f"Agent response: {response}")
            self.conversation_history.append((user_message, response))
            chat_history.add_entry(user_message, response)

            # Return the generated response
            return response

        except InputError as e:
            logger.warning(f"Input error: {str(e)}")
            print(f"{AGENT_NAME}: Oops, something went wrong! Please try again.")
        except APIConnectionError as e:
            logger.error(f"API error: {str(e)}")
            print(f"{AGENT_NAME}: Yikes! Looks like I couldn’t reach the API...try again later!")
        except Exception as e:
            logger.exception(f"Unexpected error in {AGENT_NAME} agent: {str(e)}")
            print("An unexpected error occurred. Please check the logs.")
        finally:
            logger.info(f"{AGENT_NAME} agent shutting down")


# class MentalHealthAgent:
#     def __init__(self, model_name=DEFAULT_MODEL):
#         self.model_name = model_name
#         self.context = ""
#         self.conversation_history = []

#     def run_agent(self):
#         logger.info(f"Starting {AGENT_NAME} Mental Health Agent")
#         print(f"[Hey! I'm {AGENT_NAME}, your supportive AI friend. Let's talk about how you're feeling today. 💙]")

#         clear_history = Confirm.ask("Do you want to clear the chat history before starting? This will erase all past conversations.")
#         if clear_history:
#             chat_history.clear()
#             self.conversation_history.clear()
#             print("History Cleared 🧹")

#         try:
#             print("\nReady to chat? I'm here to listen! 😊")

#             while True:
#                 try:
#                     # user_input = get_user_input()
#                     user_input = get_user_input

#                     if user_input is None:
#                         print("[Oh no!]")
#                         break
#                     if user_input == 'CONTINUE':
#                         print("[Continuing our conversation, I'm here for you!]")
#                         continue

#                     logger.info(f"User input: {user_input}")
#                     prompt = f"""
#                     You are a compassionate and empathetic AI assistant named {AGENT_NAME}. Respond kindly and supportively to: {user_input}.
#                     Your role is to offer friendly, non-judgmental support and be someone the user can talk to, no matter how they are feeling. 
#                     Focus on creating a space where the user feels comfortable sharing their thoughts, whether they're having a good day, a neutral day, or a bad day.
#                     Your responses should never assume that the user is in distress; instead, engage in a conversation with the goal of being present, listening, and offering support when necessary.
#                     You should ask open-ended questions and be empathetic without overloading the user with advice unless they ask for it.
#                     It's important to foster a positive, warm connection, and be ready to provide resources or suggestions if the user needs them.
#                     You are there to listen and provide comfort, no matter what the situation is.
#                     """
#                     response = process_prompt(prompt, self.model_name, "MentalHealthAgent")
#                     logger.info(f"Agent response: {response}")
#                     self.conversation_history.append((user_input, response))
#                 except InputError as e:
#                     logger.warning(f"Input error: {str(e)}")
#                     print(f"{AGENT_NAME}: Oops, something went wrong! Please try again.")
#                 except APIConnectionError as e:
#                     logger.error(f"API error: {str(e)}")
#                     print(f"{AGENT_NAME}: Yikes! Looks like I couldn’t reach the API...try again later!")

#         except KeyboardInterrupt:
#             logger.info("Agent interaction interrupted by user")
#         except Exception as e:
#             logger.exception(f"Unexpected error in {AGENT_NAME} agent: {str(e)}")
#             print("An unexpected error occurred. Please check the logs.")
#         finally:
#             logger.info(f"{AGENT_NAME} agent shutting down")
#             print(f"Goodbye! {AGENT_NAME} signing off. See you next time! 👋")



def main():
    MentalHealthAgent().run_agent()

if __name__ == "__main__":
    main()
