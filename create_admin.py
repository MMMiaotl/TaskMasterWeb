#!/usr/bin/env python
# -*- coding: utf-8 -*-

from app import create_app, db
from app.models import User
from werkzeug.security import generate_password_hash

def create_admin_user(username, password):
    """创建一个管理员用户"""
    app = create_app()
    with app.app_context():
        # 检查用户是否已存在
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            print(f"用户 {username} 已存在。")
            # 如果已存在但不是管理员，则设为管理员
            if not existing_user.is_admin():
                existing_user.role = 'admin'
                db.session.commit()
                print(f"已将用户 {username} 设置为管理员。")
            return

        # 创建新管理员用户
        admin_user = User(
            username=username,
            email=f"{username}@example.com",
            role='admin',
            is_active=True
        )
        admin_user.password_hash = generate_password_hash(password)
        
        # 添加到数据库
        db.session.add(admin_user)
        db.session.commit()
        print(f"管理员用户 {username} 创建成功！")

if __name__ == "__main__":
    # 创建具有管理员权限的用户，用户名为admin，密码为admin123
    create_admin_user("admin", "admin123") 