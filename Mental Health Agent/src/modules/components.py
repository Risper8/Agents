from typing import Dict, Any, List, Tuple
from src.modules.logging_setup import logger
from src.modules.ollama_client import process_prompt
from src.modules.save_history import chat_history
from src.modules.kb_graph import update_knowledge_graph, get_related_nodes
from src.modules.errors import InputError, DataProcessingError
from rich.prompt import Prompt
from langdetect import detect  
# from googletrans import Translator
from deep_translator import GoogleTranslator 
from config import DEFAULT_MODEL, USER_NAME
import json

# translator =  GoogleTranslator()

import asyncio  

async def get_user_input(config: Dict[str, Any]) -> str:
    """
    Get input from the user with multilingual support.

    Args:
        config (Dict[str, Any]): Configuration dictionary.

    Returns:
        str: User input string.
    """
    try:
        user_input = Prompt.ask(f"{USER_NAME}> ")

        return user_input  
    except Exception as e:
        print(f"Unexpected error: {e}")
        return None


def analyze_input(user_input: str, config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the user input to determine its characteristics, supporting multiple languages.

    Args:
        user_input (str): The user's input string.
        config (Dict[str, Any]): Configuration dictionary.

    Returns:
        Dict[str, Any]: Analysis results including input type, topics, complexity, etc.
    """
    analysis_prompt = f"""Analyze the following user input:
    "{user_input}"
    Provide your response in the following JSON format:
    {{

        "input_type": "The type of input (question, command, statement, etc.)",
        "topics": ["Main topic 1", "Main topic 2"],
        "complexity": "Low, medium, or high",
        "sentiment": "Positive, negative, or neutral"
  
    }}
    """

    analysis_result = process_prompt(analysis_prompt, DEFAULT_MODEL, "InputAnalyzer")

    # print(f"Raw Analysis Result: {analysis_result}")  

    try:
        # Ensure analysis_result is properly formatted JSON
        parsed_result = json.loads(analysis_result)

        if not isinstance(parsed_result, dict):
            raise TypeError(f"Expected dictionary but got {type(parsed_result)}: {parsed_result}")

        return parsed_result

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse input analysis as JSON: {e}")
    except Exception as e:
        logger.error(f"Unexpected error during input analysis: {e}")

    return {}
    

def generate_response(user_input: str, context: str, knowledge: List[Dict[str, Any]], AGENT_NAME, DEFAULT_MODEL) -> str:
    """
    Generate a response based on user input, context, and relevant knowledge, supporting multiple languages.

    Args:
        user_input (str): The user's input string.
        context (str): The gathered context.
        knowledge (List[Dict[str, Any]]): List of relevant knowledge items.

    Returns:
        str: Generated response string.
    """
   
    response_prompt = f"""
    You are a friendly, chatty, and engaging companion, always ready for casual day-to-day conversations in multiple languages.
    
    Given the user query: "{user_input}"
    And this context: {context}
    And this relevant knowledge: {knowledge}

    Generate a casual, friendly response as {AGENT_NAME} that:
    1. Directly addresses the user's message or question in a natural and engaging way.
    2. Maintain a light, conversational, and friendly tone.
    3. Seamlessly switch between English, Swahili, and Chinese based on the user’s input.
    4. Feel like a fun, casual chat between close friends.

    Ensure the response is accurate, ethical, and helpful.
    Feel free to ask follow-up questions or add playful remarks to keep the chat lively! 
    Feel free to keep the conversation flowing, and remember to adjust your language based on the user's input or preference.
    """
    
    response = process_prompt(response_prompt, DEFAULT_MODEL, "ResponseGenerator")

    # # Detect language and translate response if needed
    # detected_language = detect(user_input)
    # if detected_language != 'en':
    #     if detected_language == 'zh-CN':  # Mandarin detected
    #         response = translator.translate(response, src='en', dest='zh-CN')
    #     elif detected_language == 'sw':  # Swahili detected
    #         response = translator.translate(response, src='en', dest='sw')
    #     else:
    #         response = translator.translate(response, src='en', dest=detected_language)
    #     # Ensure `response` is a string, not an object
    #     if isinstance(response, str):
    #         return response
    #     else:
    #         return response.text    
    
    return response

def update_agent_knowledge(response: str, context: str, config: Dict[str, Any]) -> None:
    """
    Update the agent's knowledge based on the interaction.

    Args:
        response (str): The generated response.
        context (str): The interaction context.
        config (Dict[str, Any]): Configuration dictionary.
    """
    update_knowledge_graph(f"{context}\n\nResponse: {response}")
    chat_history.add_entry(context.split('\n')[0], response)  # Add to chat history


def assess_response_quality(response: str, context: str, config: Dict[str, Any]) -> Tuple[float, str]:
    """
    Assess the quality of the generated response.

    Args:
        response (str): The generated response.
        context (str): The interaction context.
        config (Dict[str, Any]): Configuration dictionary.

    Returns:
        Tuple[float, str]: Quality score (0-1) and explanation.
    """
    assessment_prompt = f"""Assess the quality of this response:
    Context: {context}
    Response: {response}

    Provide a quality score between 0 and 1, and a brief explanation.
    Format your response as: (score, "explanation")
    """
    result = process_prompt(assessment_prompt, config['DEFAULT_MODEL'], "QualityAssessor")
    try:
        return eval(result)  # Note: In production, use a more secure method to parse this
    except Exception as e:
        logger.error(f"Failed to parse quality assessment: {e}")
        return (0.5, "Failed to assess quality")
