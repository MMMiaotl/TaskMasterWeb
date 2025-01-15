import os

class Config:
    # 设置密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'