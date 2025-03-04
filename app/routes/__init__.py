from .auth import auth_bp
from .task import task_bp
from .user import user_bp
from .message import message_bp
from .main import main_bp
from .service import service_bp
from .professional import professional_bp
from ..errors import errors_bp

def init_app(app):
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(task_bp, url_prefix='/task')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(message_bp, url_prefix='/message')
    app.register_blueprint(main_bp)
    app.register_blueprint(service_bp, url_prefix='/service')
    app.register_blueprint(professional_bp)
    app.register_blueprint(errors_bp) 