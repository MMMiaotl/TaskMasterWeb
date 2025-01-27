from flask import Flask
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

# 导入路由（必须在 app 和 db 初始化之后）
from app import routes