import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration values
API_URL = os.getenv("API_URL", "http://localhost:5050")
APP_NAME = os.getenv("APP_NAME", "JuraganKlod")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
OPENAI_EMBEDDINGS_MODEL = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-large")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "adijayainc/bhsa-llama3.2")
OLLAMA_EMBEDDINGS_MODEL = os.getenv("OLLAMA_EMBEDDINGS_MODEL", "snowflake-arctic-embed2")
DATA_PATH = os.getenv("DATA_PATH", "data/")
CHROMA_PATH = os.getenv("CHROMA_PERSIST_DIR", "./chroma_langchain_sys")
CHROMA_COLLECTION = os.getenv("CHROMA_COLLECTION_NAME", "juragan_klod_collection")
WITH_OLLAMA = os.getenv("WITH_OLLAMA", "true").lower() == "true"