from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timezone

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 评价内容
    rating = db.Column(db.Integer, nullable=False)  # 评分（例如 1-5 分）
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 评价人
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 被评价人
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)  # 关联的任务
    role = db.Column(db.String(20), nullable=False)  # 评价角色（'poster' 或 'executor'）
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    # 关系
    reviewer = db.relationship('User', foreign_keys=[reviewer_id], backref='reviews_given')  # 评价人
    reviewee = db.relationship('User', foreign_keys=[reviewee_id], backref='reviews_received')  # 被评价人
    task = db.relationship('Task', backref='reviews')  # 关联的任务
    
class User(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    tasks = db.relationship('Task', backref='user', lazy='dynamic')  # 定义与 Task 的关系


    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(140))
    description = db.Column(db.Text)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))  # 添加 created_at 字段


    def __repr__(self):
        return '<Task {}>'.format(self.title)
    
class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)  # 私信内容
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 发送者
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 接收者
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)  # 关联的任务
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))  # 发送时间

    # 关系
    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_messages')
    recipient = db.relationship('User', foreign_keys=[recipient_id], backref='received_messages')
    task = db.relationship('Task', backref='messages')