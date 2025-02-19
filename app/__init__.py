from flask import Flask, request, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_babel import Babel
from flask_migrate import Migrate

# 创建 Flask 应用实例
app = Flask(__name__)

# 加载配置
app.config.from_object('config.Config')

# 初始化 Flask-Babel
babel = Babel(app)

# 实现语言选择函数
def get_locale():
    # 按优先级获取语言设置：
    # 1. URL 参数
    # 2. 用户会话设置
    # 3. 浏览器请求头
    # 4. 默认语言
    if request.args.get('lang'):
        return request.args.get('lang')
    elif 'lang' in session:
        return session['lang']
    return request.accept_languages.best_match(app.config['BABEL_SUPPORTED_LOCALES'])

# 设置语言选择器
babel.locale_selector_func = get_locale

# 初始化数据库
db = SQLAlchemy(app)
# 初始化 Flask-Migrate
migrate = Migrate(app, db)

# 初始化登录管理器
login = LoginManager(app)
login.login_view = 'login'

# 导入用户模型
from app.models import User

# 实现 user_loader 回调函数
@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# 导入并注册蓝图
from app.routes import init_app as init_routes
init_routes(app)
