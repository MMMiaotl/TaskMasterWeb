from flask import Blueprint, redirect, url_for, current_app, session, flash, request
from flask_login import login_user, current_user
from authlib.integrations.flask_client import OAuth
from app import db
from app.models import User
import json
from datetime import datetime, timedelta

oauth_bp = Blueprint('oauth', __name__)

# 初始化OAuth
oauth = OAuth()

# 配置Google OAuth
def setup_oauth(app):
    oauth.init_app(app)
    oauth.register(
        name='google',
        client_id=app.config.get('GOOGLE_CLIENT_ID'),
        client_secret=app.config.get('GOOGLE_CLIENT_SECRET'),
        server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
        client_kwargs={
            'scope': 'openid email profile'
        }
    )

@oauth_bp.route('/login/google')
def login_google():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    
    redirect_uri = url_for('oauth.google_callback', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@oauth_bp.route('/login/google/callback')
def google_callback():
    try:
        token = oauth.google.authorize_access_token()
        user_info = oauth.google.parse_id_token(token)
        
        # 获取用户信息
        email = user_info.get('email')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        
        # 检查邮箱是否已验证
        if not user_info.get('email_verified'):
            flash('您的谷歌邮箱未验证，请先验证邮箱后再尝试登录。')
            return redirect(url_for('auth.login'))
        
        # 查找或创建用户
        user = User.query.filter_by(email=email).first()
        if not user:
            # 创建新用户
            username = name.replace(' ', '') + str(datetime.utcnow().strftime('%f'))[:4]
            user = User(
                username=username,
                email=email,
                email_confirmed=True,  # 谷歌账号的邮箱已经验证过
                avatar_url=picture,
                oauth_provider='google',
                oauth_id=user_info.get('sub')
            )
            # 设置随机密码（用户无法使用密码登录，只能通过谷歌登录）
            import secrets
            random_password = secrets.token_urlsafe(16)
            user.set_password(random_password)
            
            db.session.add(user)
            db.session.commit()
            flash('您的账号已通过谷歌账号创建成功！')
        else:
            # 更新现有用户的OAuth信息
            if not user.oauth_provider:
                user.oauth_provider = 'google'
                user.oauth_id = user_info.get('sub')
                user.avatar_url = picture
                db.session.commit()
        
        # 登录用户
        login_user(user)
        next_page = request.args.get('next')
        if not next_page or next_page.startswith('/'):
            next_page = url_for('main.index')
        
        return redirect(next_page)
    except Exception as e:
        current_app.logger.error(f'Google OAuth登录失败: {str(e)}')
        flash('登录失败，请稍后再试。')
        return redirect(url_for('auth.login')) 