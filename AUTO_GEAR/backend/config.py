import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory: AUTO_GEAR root
BASE_DIR = Path(__file__).resolve().parent.parent

# Load .env file from AUTO_GEAR root
load_dotenv(BASE_DIR / ".env")


class Config:
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "autogear_dev_secret_key_2026")
    DEBUG = os.getenv("FLASK_DEBUG", "True").lower() in ("true", "1", "t")

    # MySQL database settings
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = int(os.getenv("DB_PORT", 3306))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "autogear_db")
