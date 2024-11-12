import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    APP_PORT = os.getenv('APP_PORT')
    API_CREDENTIALS = os.getenv('API_CREDENTIALS')
    USERNAME = os.getenv('LOGIN_USERNAME')
    PASSWORD = os.getenv('LOGIN_PASSWORD')
    SECRET_KEY = os.getenv('SECRET_KEY')