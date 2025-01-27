from app import app, db

# 创建应用上下文
with app.app_context():
    db.create_all()  # 创建数据库表

if __name__ == '__main__':
    app.run(debug=True)