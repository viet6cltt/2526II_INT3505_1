import os 
from dotenv import load_dotenv


load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "super_secret_key")
    ACCESS_TOKEN_EXPIRES_IN = int(os.getenv("ACCESS_TOKEN_EXPIRES_IN", 3600))
    REFRESH_TOKEN_EXPIRES_IN = int(os.getenv("REFRESH_TOKEN_EXPIRES_IN", 86400))
    SQLALCHEMY_DATABASE_URI = "sqlite:///app.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = os.getenv("LOG_FORMAT", "json")
    WERKZEUG_LOG_LEVEL = os.getenv("WERKZEUG_LOG_LEVEL", "WARNING")
    NOTIFICATION_SERVICE_URL = os.getenv(
        "NOTIFICATION_SERVICE_URL",
        "http://127.0.0.1:5003"
    )
