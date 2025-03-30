# from langdetect import detect
# from transformers import MarianMTModel, MarianTokenizer
# import random

# # Load translation models
# def load_translation_models():
#     return {
#         "en_to_xx": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-en-ROMANCE"),
#         "xx_to_en": MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-ROMANCE-en"),
#         "en_tokenizer": MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-en-ROMANCE"),
#         "xx_tokenizer": MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ROMANCE-en"),
#     }

# models = load_translation_models()

# # Simple conversation history
# conversation_history = {}

# # Function to translate text
# def translate_text(text, model, tokenizer):
#     inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
#     translated = model.generate(**inputs)
#     return tokenizer.decode(translated[0], skip_special_tokens=True)

# # Generate a basic AI response (for demo purposes)
# def generate_response(text):
#     responses = [
#         "That's interesting! Tell me more.",
#         "I see! What else would you like to discuss?",
#         "That's a great point! Any other thoughts?",
#     ]
#     return random.choice(responses)

# # Main chatbot function
# def multilingual_chatbot(user_id, user_input):
#     user_language = detect(user_input)  # Detect language
#     conversation_history.setdefault(user_id, [])  # Initialize user history

#     if user_language != "en":  # Translate input to English if needed
#         user_input = translate_text(user_input, models["xx_to_en"], models["xx_tokenizer"])
    
#     response = generate_response(user_input)  # Generate response

#     if user_language != "en":  # Translate response back to user's language
#         response = translate_text(response, models["en_to_xx"], models["en_tokenizer"])

#     conversation_history[user_id].append((user_input, response))  # Store conversation history

#     return response

# # Example usage
# user_id = "user_123"  # Unique ID for user session
# user_input = "Bonjour, comment vas-tu?"  # Input in French
# bot_response = multilingual_chatbot(user_id, user_input)
# print(f"Bot: {bot_response}")

# from dotenv import load_dotenv
# import os

# load_dotenv()

# VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")

# if VERIFICATION_TOKEN is None:
#     print("VERIFICATION_TOKEN is not set!")
# else:
#     print(f"VERIFICATION_TOKEN is set to: {VERIFICATION_TOKEN}")

