from flask import request, g, current_app
from datetime import datetime, timezone
from flask_login import current_user

def before_request():
    g.request_start_time = datetime.now(timezone.utc)
    if current_user.is_authenticated:
        current_user.update_last_seen()

def after_request(response):
    # 添加安全头
    for header, value in current_app.config['SECURE_HEADERS'].items():
        response.headers[header] = value
    return response 