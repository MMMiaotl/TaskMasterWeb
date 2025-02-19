from .auth import auth_bp
from .task import task_bp
from .user import user_bp
from .message import message_bp
from .main import main_bp

def init_app(app):
    app.register_blueprint(auth_bp)
    app.register_blueprint(task_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(message_bp)
    app.register_blueprint(main_bp) 