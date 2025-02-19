from functools import wraps
from flask import abort, request, current_app
import hmac
import hashlib

def csrf_protect():
    """CSRF保护装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method == "POST":
                token = request.form.get('csrf_token')
                if not token or not check_csrf_token(token):
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def check_csrf_token(token):
    """验证CSRF令牌"""
    secret_key = current_app.config['SECRET_KEY']
    return hmac.compare_digest(
        token,
        generate_csrf_token(secret_key)
    )

def generate_csrf_token(secret_key):
    """生成CSRF令牌"""
    return hashlib.sha256(secret_key.encode()).hexdigest() 