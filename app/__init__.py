from flask import Flask, request, session, g, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate
from app.filters import status_translate
from config import Config

# 创建实例
db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
babel = Babel()

def get_locale():
    # 添加调试日志
    print(f"Current session language: {session.get('language')}")
    print(f"Available languages: {current_app.config['BABEL_SUPPORTED_LOCALES']}")
    
    if 'language' in session:
        print(f"Using session language: {session['language']}")
        return session['language']
    
    # 默认返回中文
    return 'zh'

def create_app():
    app = Flask(__name__)
    
    # 配置导入
    app.config.from_object(Config)
    
    # 初始化扩展
    db.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app, locale_selector=get_locale)
    migrate.init_app(app, db)
    
    # 添加模板上下文
    @app.context_processor
    def inject_template_globals():
        return {
            'get_locale': get_locale,
            'current_language': session.get('language', 'zh')
        }
    
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

    # 将配置添加到模板全局变量
    @app.context_processor
    def inject_config():
        return dict(config=app.config)
    
    # 添加调试中间件
    @app.after_request
    def print_session(response):
        if app.debug:  # 直接使用app对象而不是current_app
            from flask import session
            print(f"[DEBUG] Session contents: {dict(session)}")
            print(f"[DEBUG] Response headers: {response.headers}")
        return response

    return app

# 用户加载函数
@login_manager.user_loader
def load_user(id):
    from app.models import User
    return User.query.get(int(id))

# 确保导出必要的名称
__all__ = ['create_app', 'db', 'login_manager', 'babel', 'migrate']
