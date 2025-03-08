import os
from datetime import timedelta

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # 基础配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'complex-key-here'
    BASEDIR = basedir
    
    # 安全配置
    REMEMBER_COOKIE_DURATION = timedelta(days=30)
    REMEMBER_COOKIE_SECURE = True
    REMEMBER_COOKIE_HTTPONLY = True
    SESSION_COOKIE_NAME = 'taskmaster_session'
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = False  # 开发环境可关闭
    SESSION_COOKIE_SAMESITE = 'Lax'  # 保持与之前一致
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)
    SESSION_REFRESH_EACH_REQUEST = True
    
    # CSRF保护配置
    WTF_CSRF_ENABLED = True
    WTF_CSRF_SECRET_KEY = os.environ.get('WTF_CSRF_SECRET_KEY') or 'csrf-secret-key'
    WTF_CSRF_TIME_LIMIT = 3600  # CSRF令牌1小时有效
    WTF_CSRF_SSL_STRICT = False  # 开发环境可关闭
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'instance', 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Babel配置
    BABEL_DEFAULT_LOCALE = 'zh'
    BABEL_SUPPORTED_LOCALES = ['zh', 'en']
    BABEL_TRANSLATION_DIRECTORIES = 'translations'
    
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

    # 添加调试模式
    DEBUG = True

    # 修改默认站点名称
    SITE_NAME = 'Helpers'
    SITE_NAME_CN = '海帮'

    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static', 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    # 添加货币配置
    CURRENCY_SYMBOL = '€'  # 新增配置项
    CURRENCY_CODE = 'EUR'  # ISO货币代码

    SESSION_TYPE = 'filesystem'  # 如果需要服务端存储
    
    # 邮件配置
    MAIL_SERVER = 'localhost'
    MAIL_PORT = 1025
    MAIL_USE_TLS = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None
    MAIL_DEFAULT_SENDER = 'noreply@haibang.com'
    MAIL_SUBJECT_PREFIX = '[海帮] '
    
    # 应用基础URL，用于生成确认链接等
    BASE_URL = 'http://localhost:5000'  # 本地测试用
    
    # 邮箱验证配置
    EMAIL_VERIFICATION_REQUIRED = False  # 开发环境默认禁用邮箱验证

class DevelopmentConfig(Config):
    # 开发环境特定配置
    DEBUG = True
    TESTING = False
    EMAIL_VERIFICATION_REQUIRED = False  # 开发环境禁用邮箱验证
    
class ProductionConfig(Config):
    # 生产环境特定配置
    DEBUG = False
    TESTING = False
    EMAIL_VERIFICATION_REQUIRED = True  # 生产环境启用邮箱验证 