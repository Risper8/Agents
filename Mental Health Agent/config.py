import os
from pathlib import Path

# User and Agent configuration
USER_NAME = os.getenv("USER_NAME", "Risper")
AGENT_NAME = os.getenv("AI_AGENT_NAME", "Pal")

# Model configuration
# DEFAULT_MODEL = "llama3.1:latest"
DEFAULT_MODEL = 'gemma:2b'
EMBEDDING_MODEL = os.getenv("AI_EMBEDDING_MODEL", "nomic-embed-text")

# Memory configuration
MEMORY_LENGTH = int(os.getenv("AI_MEMORY_LENGTH", "15"))
CHUNK_SIZE = int(os.getenv("AI_CHUNK_SIZE", "5000"))
CHUNK_OVERLAP = int(os.getenv("AI_CHUNK_OVERLAP", "200"))
CHUNK_LENGTH = int(os.getenv("AI_CHUNK_LENGTH", "10"))

# Path configuration
PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data" / "json_history"
EMBEDDINGS_DIR = DATA_DIR / "embeddings"


# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
EMBEDDINGS_DIR.mkdir(parents=True, exist_ok=True)


# File paths
CHAT_HISTORY_FILE = PROJECT_ROOT/ ".chat_history.json"

# Search configuration
DEFAULT_TOP_K = int(os.getenv("AI_DEFAULT_TOP_K", "5"))
DEFAULT_SIMILARITY_THRESHOLD = float(os.getenv("AI_DEFAULT_SIMILARITY_THRESHOLD", "0.0"))

# Logging configuration
LOG_LEVEL = os.getenv("AI_LOG_LEVEL", "WARNING")
LOG_FILE = PROJECT_ROOT / "logs" / "ollama_agents.log"

# Ensure log directory exists
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)

# Assistant command configurations
DEFAULT_BROWSER = "default"

#Database Settings
