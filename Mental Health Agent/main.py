import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from routes.whatsapp_route import router as whatsapp_router


load_dotenv()

IS_DEV_ENVIRONMENT = os.getenv("IS_DEV_ENVIRONMENT", "False").lower() == "true"

# Create main FastAPI app
app = FastAPI(
    title="WhatsApp Chatbot API",
    version="1.0",
    openapi_url="/openapi.json" if IS_DEV_ENVIRONMENT else None,
    docs_url="/docs" if IS_DEV_ENVIRONMENT else None,
    redoc_url="/redoc" if IS_DEV_ENVIRONMENT else None,
)

app.include_router(whatsapp_router)

# if __name__ == "__main__":
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
    # uvicorn.run("main:app", host="localhost", port=8000, reload=True)
