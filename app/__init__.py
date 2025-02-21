from flask import Flask, request, session, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate
from app.filters import status_translate

# 创建实例
db = SQLAlchemy()
login_manager = LoginManager()
babel = Babel()
migrate = Migrate()

def get_locale():
    return request.accept_languages.best_match(['zh', 'en'])

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
    
    # 设置登录视图
    login_manager.login_view = 'auth.login'
    login_manager.login_message = '请先登录。'
    
    # 注册蓝图
    from app.routes import init_app as init_routes
    init_routes(app)
    
    # 添加自定义Jinja过滤器
    #@app.template_filter('merge')
    #@pass_context
    #def merge_filter(ctx, d, u):
    #    d.update(u)
    #    return d

    #@app.template_filter('another_filter')
    #@pass_context
    #def another_filter(ctx, value):
        # 过滤器逻辑
    #    return modified_value

    from app.routes.task import task_bp

    # 定义 status_translate 过滤器
    @app.template_filter('status_translate')
    def status_translate(status):
        translations = {
            'open': 'Open',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return translations.get(status, status)

    app.jinja_env.filters['status_translate'] = status_translate

    return app

# 用户加载函数
@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

# 创建应用实例
app = create_app()

# 确保导出必要的名称
__all__ = ['create_app', 'db', 'login_manager', 'babel', 'migrate']
