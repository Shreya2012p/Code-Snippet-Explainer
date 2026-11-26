# Import os to access environment variables
import os

# Import Path to handle file and directory paths
from pathlib import Path

# Import load_dotenv to load configuration values from the .env file
from dotenv import load_dotenv


# Get the project root directory (two levels above the current file)
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from the project's .env file
load_dotenv(BASE_DIR / ".env")


# Application name displayed or used within the CodeWise AI project
APP_NAME = "CodeWise AI — Advanced Code Intelligence"


# Ollama server URL used to communicate with the locally running AI model
# Uses the .env value if available; otherwise, uses the default local address
OLLAMA_BASE_URL = os.getenv(
    "OLLAMA_BASE_URL",
    "http://127.0.0.1:11434"
)


# Name of the AI model used for code analysis
# Defaults to Qwen 2.5 Coder with 7 billion parameters
OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "qwen2.5-coder:7b"
)



# Webhook URL used to send code analysis reports to the n8n workflow
# An empty string is used if no webhook URL is configured
N8N_WEBHOOK_URL = os.getenv(
    "N8N_WEBHOOK_URL",
    ""
)


# Maximum time in seconds allowed for an AI request
# Defaults to 180 seconds (3 minutes)
REQUEST_TIMEOUT = int(
    os.getenv("REQUEST_TIMEOUT", "180")
)