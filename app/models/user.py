from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import func
import secrets
import time

# 用户与专业类别的多对多关系表
user_categories = db.Table('user_categories',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('category_id', db.String(50), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user', 'professional' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    location = db.Column(db.String(64))
    website = db.Column(db.String(128))
    avatar_url = db.Column(db.String(200))  # 用户头像URL
    
    # 邮箱验证相关字段
    email_confirmed = db.Column(db.Boolean, default=False)
    email_confirm_token = db.Column(db.String(100))
    email_confirm_sent_at = db.Column(db.DateTime)
    
    # 专业人士额外字段
    is_professional = db.Column(db.Boolean, default=False)
    professional_title = db.Column(db.String(64))  # 专业人士头衔
    professional_summary = db.Column(db.Text)  # 专业简介
    experience_years = db.Column(db.Integer)  # 经验年数
    hourly_rate = db.Column(db.Float)  # 每小时费率
    skills = db.Column(db.String(200))  # 技能列表，以逗号分隔
    certifications = db.Column(db.Text)  # 资质证书
    
    # 专业类别关系
    categories = db.relationship('UserCategory', back_populates='user', cascade='all, delete-orphan')
    
    # 关系
    tasks = db.relationship('Task', foreign_keys='Task.user_id', backref='author', lazy='dynamic')
    sent_messages = db.relationship(
        'Message',
        primaryjoin="User.id==Message.sender_id",
        backref=db.backref('sender', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    received_messages = db.relationship(
        'Message',
        primaryjoin="User.id==Message.recipient_id",
        backref=db.backref('recipient', lazy='joined'),
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    invited_tasks = db.relationship(
        'Task',
        secondary='messages',
        primaryjoin="and_(Message.recipient_id==User.id, Message.is_invitation==True)",
        secondaryjoin="Message.task_id==Task.id",
        viewonly=True,
        lazy='dynamic'
    )

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_pro(self):
        return self.is_professional
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    # 检查用户是否有特定类别的专业资格
    def has_category(self, category_id):
        return any(cat.category_id == category_id for cat in self.categories)
    
    # 获取用户的所有专业类别ID
    def get_category_ids(self):
        return [cat.category_id for cat in self.categories]
    
    @property
    def rating(self):
        """计算用户的平均评分"""
        from app.models import Review
        result = db.session.query(func.avg(Review.rating)).filter(
            Review.reviewee_id == self.id
        ).scalar()
        return round(result, 1) if result else 0
    
    @property
    def completed_tasks(self):
        """获取用户完成的任务数量"""
        from app.models import Task
        if self.is_professional:
            # 作为执行者完成的任务
            return Task.query.filter_by(executor_id=self.id, status=2).count()
        else:
            # 作为发布者完成的任务
            return Task.query.filter_by(user_id=self.id, status=2).count()
    
    def generate_email_token(self):
        """生成邮箱验证令牌"""
        self.email_confirm_token = secrets.token_hex(32)
        self.email_confirm_sent_at = datetime.utcnow()
        return self.email_confirm_token
    
    def confirm_email(self, token):
        """确认邮箱验证令牌"""
        if token == self.email_confirm_token:
            self.email_confirmed = True
            self.email_confirm_token = None
            return True
        return False
    
    def token_expired(self, expiration=3600):
        """检查令牌是否过期，默认1小时过期"""
        if self.email_confirm_sent_at is None:
            return True
        now = datetime.utcnow()
        diff = now - self.email_confirm_sent_at
        return diff.total_seconds() > expiration
    
    def __repr__(self):
        return f'<User {self.username}>'

class UserCategory(db.Model):
    __tablename__ = 'user_category'
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    category_id = db.Column(db.String(50), primary_key=True)  # 存储格式为 "main_category.sub_category"
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 关系
    user = db.relationship('User', back_populates='categories') 