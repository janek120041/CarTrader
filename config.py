import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.urandom(32)  # Generate a secure random secret key
    SQLALCHEMY_DATABASE_URI = 'sqlite:///cartrader.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join('app', 'static', 'car_images')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size 