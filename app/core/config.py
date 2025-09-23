import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MONETBIL_SERVICE_KEY: str
    MONETBIL_SECRET_KEY: str
    MONETBIL_API_URL: str = "https://api.monetbil.com/widget/v2.1"

settings = Settings()
