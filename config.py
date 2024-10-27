import os
from dotenv import load_dotenv

env_path = os.path.join('.env', '.env')
load_dotenv(dotenv_path=env_path)

class Config:
    # SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    APP_PORT = os.getenv('APP_PORT')
    API_CREDENTIALS = os.getenv('API_CREDENTIALS')
