import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

# Configuration values
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "janitrapanji")
DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "kangserver")
DB_PORT = os.getenv("DB_PORT", "5432")
XENDIT_API_KEY = os.getenv("XENDIT_API_KEY", "xnd_development_...")