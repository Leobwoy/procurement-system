import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your_secret_key_here'  # You can change this to something secret
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///instance/procurement_system.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
