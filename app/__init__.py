from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate
import os, sys

# 创建实例
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    
    # 配置导入
    from config import Config
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    migrate.init_app(app, db)
    
    with app.app_context():
        # 确保所有模型都已导入
        from app.models import User, Task, Message, Review
        # 创建所有表
        db.create_all()
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录。'
    
    # 注册中间件
    from .middleware import before_request, after_request
    app.before_request(before_request)
    app.after_request(after_request)
    
    # 注册蓝图
    from app.routes import init_app as init_routes
    init_routes(app)
    
    return app

# 用户加载函数
@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

# 语言选择函数
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'zh')

# 创建应用实例
app = create_app()

# 确保导出必要的名称
__all__ = ['create_app', 'db', 'login_manager', 'babel', 'migrate']
