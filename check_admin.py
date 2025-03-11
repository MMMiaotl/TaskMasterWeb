from app import create_app, db
from app.models import User

app = create_app()
with app.app_context():
    admin_users = User.query.filter_by(role='admin').all()
    print(f'管理员账户数量: {len(admin_users)}')
    for user in admin_users:
        print(f'管理员: {user.username}, 邮箱: {user.email}') 