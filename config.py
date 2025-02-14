import os

class Config:
    # 默认语言
    BABEL_DEFAULT_LOCALE = 'en'
    # 支持的语言列表
    BABEL_SUPPORTED_LOCALES = ['zh', 'en']
    
    BABEL_TRANSLATION_DIRECTORIES = os.path.join(os.path.dirname(__file__), 'translations')  # 翻译文件目录

    # 设置密钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    # 设置数据库连接
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 禁用跟踪修改，避免警告