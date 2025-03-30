# src/modules/context_management.py

import json
from typing import List, Dict, Any
from src.modules.memory_search import search_memories
from src.modules.logging_setup import logger
from src.modules.errors import DataProcessingError
from src.modules.ollama_client import process_prompt

def gather_context(user_input: str, conversation_history: List[Dict[str, str]], agent_name: str) -> str:
    """
    Gather context from various sources for a given user input.
    """
    try:
        # Retrieve relevant memories
        memories = search_memories(user_input, top_k=3, similarity_threshold=0.7)
        memory_context = "\n".join([f"💾 Related info: {m['content']}" for m in memories])

        # Get recent conversation history
        recent_history = conversation_history[-3:]
        history_context = "\n".join(
            [f"👤 User: {h[0] if isinstance(h, tuple) else h.get('prompt', '')}\n🤖 {agent_name}: {h[1] if isinstance(h, tuple) else h.get('response', '')}" 
             for h in recent_history]
        )
        # history_context = "\n".join([f"👤 User: {h.get('prompt', '')}\n🤖 {agent_name}: {h.get('response', '')}" for h in recent_history])

        # Combine all context
        full_context = f"📚 Relevant information:\n{memory_context}\n\n💬 Recent conversation:\n{history_context}\n\n"

        logger.info("Context gathering completed successfully")
        return full_context
    except Exception as e:
        logger.error(f"Error gathering context: {str(e)}")
        raise DataProcessingError(f"Failed to gather context: {str(e)}")

def update_context(current_context: str, new_information: str, model_name: str) -> str:
    """
    Update the current context with new information.
    """
    try:
        logger.info("Updating context with new information")
        update_prompt = f"""Update the following context with the new information:

        Current Context:
        {current_context}

        New Information:
        {new_information}

        Provide an updated context that incorporates the new information coherently.
        """
        return process_prompt(update_prompt, model_name, "ContextUpdater")
    except Exception as e:
        logger.error(f"Error updating context: {str(e)}")
        return current_context  # Return original context if update fails


def adapt_context_to_user(context: str, model_name: str) -> str:
    """
    Adapt the context to a specific user's profile and preferences.
    """
    try:
        logger.info("Adapting context to user profile")
        adapt_prompt = f"""Adapt the following context to continue a supportive, engaging, and empathetic conversation with the user, ensuring that the flow remains natural:

        Context:
        {context}

        Ensure the adaptation remains compassionate, maintains the integrity of the conversation, and keeps it flowing naturally, while being sensitive to the user's emotional needs.

        """
        return process_prompt(adapt_prompt, model_name, "ContextAdapter")
    except Exception as e:
        logger.error(f"Error adapting context to user: {str(e)}")
        return context  