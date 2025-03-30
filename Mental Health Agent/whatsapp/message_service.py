import os
import json
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from typing import BinaryIO
from src.agents.simple_agent import MentalHealthAgent
from whatsapp.schema import Audio, User
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv(override=True)

WHATSAPP_API_KEY = os.getenv('TEST_ACCESS_TOKEN')
VERSION = os.getenv('VERSION')
PHONE_NUMBER_ID = os.getenv('PHONE_NUMBER_ID')
OPENAI_API_KEY = os.getenv('api_key')


llm = OpenAI(api_key=OPENAI_API_KEY)

# Initialize the MentalHealthAgent 
agent = MentalHealthAgent()


# processing and transcribing audio 
def transcribe_audio_file(audio_file: BinaryIO) -> str:
    if not audio_file:
        return "No audio file provided"
    try:
        transcription = llm.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="text"
        )
        return transcription
    except Exception as e:
        raise ValueError("Error transcribing audio") from e

def transcribe_audio(audio: Audio) -> str:
    file_path = download_file_from_facebook(audio.id, "audio", audio.mime_type)
    with open(file_path, 'rb') as audio_binary:
        transcription = transcribe_audio_file(audio_binary)
    try:
        os.remove(file_path)
    except Exception as e:
        print(f"Failed to delete file: {e}")
    return transcription

def download_file_from_facebook(file_id: str, file_type: str, mime_type: str) -> str | None:
    # First GET request to retrieve the download URL
    url = f"https://graph.facebook.com/v{VERSION}/{file_id}"
    headers = {"Authorization": f"Bearer {WHATSAPP_API_KEY}"}
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        download_url = response.json().get('url')

        # Second GET request to download the file
        response = requests.get(download_url, headers=headers)

        if response.status_code == 200:
            file_extension = mime_type.split('/')[-1].split(';')[0]  # Extract file extension from mime_type
            file_path = f"{file_id}.{file_extension}"
            with open(file_path, 'wb') as file:
                file.write(response.content)
            if file_type == "image" or file_type == "audio":
                return file_path

        raise ValueError(f"Failed to download file. Status code: {response.status_code}")
    raise ValueError(f"Failed to retrieve download URL. Status code: {response.status_code}")

## User authentication
def authenticate_user_by_phone_number(phone_number: str) -> User | None:
    allowed_users = [
        {"id": 1, "phone": "254714699354", "first_name": "Risper", "last_name": "Ndirangu", "role": "user"},
        {"id": 2, "phone": "254794203829", "first_name": "Jackline", "last_name": "Wangui", "role": "user"}
    ]

    sanitized_phone_number = sanitize_phone_number(phone_number)
    print(f"Sanitized phone number: {sanitized_phone_number}")

    for user in allowed_users:
        print(f"Checking user: {user['phone']} with sanitized number")
        if user["phone"] == sanitized_phone_number:
            return User(**user)
    return None


def sanitize_phone_number(phone_number: str) -> str:
    return phone_number.replace(" ", "").replace("-", "")

## sending message to the user
def send_whatsapp_message(to, message, template=True):
    print(f"Sending message to {to} with content: {message}")  # Debugging log
    url = f"https://graph.facebook.com/v{VERSION}/569430986259047/messages"
    print(url)
    headers = {
        "Authorization": f"Bearer {WHATSAPP_API_KEY}",
        "Content-Type": "application/json"
    }

    if not template:
        data = {
            "messaging_product": "whatsapp",
            "preview_url": False,
            "recipient_type": "individual",
            "to": to,
            "type": "text",
            "text": {
                "body": message
            }
        }
    else:
        data = {
            "messaging_product": "whatsapp",
            "to": to,
            "type": "template",
            "template": {
                "name": "hello",
                "language": {
                    "code": "en_US"
                }
            }
        }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    # Log the response to check for errors
    # print(f"Response status code: {response.status_code}")
    # print(f"Response content: {response.text}")

    if response.status_code == 200:
        print("Message sent successfully!")
    else:
        print(f"Error sending message: {response.status_code}, {response.text}")  
    
    return response.json()


def respond_and_send_message(user_message: str, user: User):
    if user_message is None:
        return "No message provided"
    response = agent.run_agent(user_message, user.id) 
    send_whatsapp_message(user.phone, response, template=False)
    # print(f"Sent message to user {user.first_name} {user.last_name} ({user.phone})")
    # print(f"Message: {response}")



if __name__ == "__main__":
    response = agent.run_agent()
    print(response) 
