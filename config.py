import os
from datetime import timedelta

class Config:
    # 基础配置
    SECRET_KEY = 'dev'
    BASEDIR = os.path.abspath(os.path.dirname(__file__))
    
    # 安全配置
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASEDIR, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Babel配置
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_SUPPORTED_LOCALES = ['en', 'zh']
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(BASEDIR, 'app/translations')
    
    # 安全头部配置
    SECURE_HEADERS = {
        'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
        'X-Content-Type-Options': 'nosniff',
        'X-Frame-Options': 'SAMEORIGIN',
        'X-XSS-Protection': '1; mode=block',
    }
    
    # 分页配置
    TASKS_PER_PAGE = 10
    MESSAGES_PER_PAGE = 20