from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# 创建 Flask 应用实例
app = Flask(__name__)

# 加载配置
app.config.from_object('config')

# 初始化数据库
db = SQLAlchemy(app)

# 初始化登录管理器
login = LoginManager(app)
login.login_view = 'login'

# 导入路由（必须在 app 和 db 初始化之后）
from app import routes