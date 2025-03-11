from app import create_app, db
from app.models import User
from datetime import datetime

app = create_app()
with app.app_context():
    # 检查是否已存在管理员账户
    admin = User.query.filter_by(role='admin').first()
    
    if admin:
        print(f'已存在管理员账户: {admin.username}, 邮箱: {admin.email}')
    else:
        # 检查是否存在用户名为 admin 的用户
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            # 将现有用户更新为管理员
            admin_user.role = 'admin'
            admin_user.email_confirmed = True
            db.session.commit()
            print(f'已将用户 {admin_user.username} 更新为管理员角色')
            print(f'邮箱: {admin_user.email}')
        else:
            # 创建新的管理员账户
            admin = User(
                username='admin',
                email='admin@example.com',
                role='admin',
                email_confirmed=True,
                created_at=datetime.utcnow()
            )
            admin.set_password('admin123')  # 设置密码
            
            # 保存到数据库
            db.session.add(admin)
            db.session.commit()
            
            print(f'成功创建管理员账户: {admin.username}, 邮箱: {admin.email}')
            print('请使用以下凭据登录:')
            print('用户名: admin')
            print('密码: admin123') 