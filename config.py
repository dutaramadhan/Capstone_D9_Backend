import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    APP_PORT = os.getenv('APP_PORT')
