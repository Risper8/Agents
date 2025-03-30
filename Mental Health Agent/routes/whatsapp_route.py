from fastapi import FastAPI, Query, HTTPException, Depends, APIRouter
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import threading
# import uvicorn
from dotenv import load_dotenv
from whatsapp import message_service
from whatsapp.schema import Payload, Message, Audio, Image, User
from typing_extensions import Annotated

load_dotenv()

VERIFICATION_TOKEN = os.getenv("VERIFICATION_TOKEN")
IS_DEV_ENVIRONMENT = os.getenv("IS_DEV_ENVIRONMENT", "False").lower() == "true"

router = APIRouter()

@router.get("/")
def verify_whatsapp(
    hub_mode: str = Query("subscribe", description="The mode of the webhook", alias="hub.mode"),
    hub_challenge: int = Query(..., description="The challenge to verify the webhook", alias="hub.challenge"),
    hub_verify_token: str = Query(..., description="The verification token", alias="hub.verify_token"),
):
    print(f"Received parameters: hub_mode={hub_mode}, hub_challenge={hub_challenge}, hub_verify_token={hub_verify_token}")
    
    if hub_mode == "subscribe" and hub_verify_token == VERIFICATION_TOKEN:
        return hub_challenge
    raise HTTPException(status_code=403, detail="Invalid verification token")


def parse_message(payload: Payload) -> Message | None:  
    if not payload.entry[0].changes[0].value.messages:  
        return None  
    return payload.entry[0].changes[0].value.messages[0]  

def get_current_user(message: Annotated[Message, Depends(parse_message)]) -> User | None:  
    if not message:  
        return None  
    return message_service.authenticate_user_by_phone_number(message.from_)  

def parse_audio_file(message: Annotated[Message, Depends(parse_message)]) -> Audio | None:  
    if message and message.type == "audio":  
        return message.audio  
    return None  

def parse_image_file(message: Annotated[Message, Depends(parse_message)]) -> Image | None:  
    if message and message.type == "image":  
        return message.image  
    return None  

def message_extractor(  
        message: Annotated[Message, Depends(parse_message)],  
        audio: Annotated[Audio, Depends(parse_audio_file)],  
):  
    if audio:  
        return message_service.transcribe_audio(audio)  
    if message and message.text:  
        return message.text.body  
    return None

@router.post("/", status_code=200)
def receive_whatsapp(
        user: Annotated[User, Depends(get_current_user)],
        user_message: Annotated[str, Depends(message_extractor)],
        image: Annotated[Image, Depends(parse_image_file)],
):
    if not user and not user_message and not image:
        # status message
        return {"status": "ok"}

    if not user:
        raise HTTPException(status_code=401, detail="Unauthorized")

    if image:
        return print("Image received")

    if user_message:
        print(f"Received message from user {user.first_name} {user.last_name} ({user.phone})")
        thread = threading.Thread(target=message_service.respond_and_send_message, args=(user_message, user))
        thread.daemon = True
        thread.start()
    return {"status": "ok"}



