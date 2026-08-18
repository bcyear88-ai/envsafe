import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

class Config:
    SECRET_KEY = 'envsafe-secret-key-2025-cement'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "envsafe.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'jwt-secret-envsafe-2025'
    JWT_ACCESS_TOKEN_EXPIRES = 86400
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
