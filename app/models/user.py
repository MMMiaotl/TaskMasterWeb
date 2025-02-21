from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), default='user')  # 'user' or 'admin'
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    phone = db.Column(db.String(20))
    bio = db.Column(db.Text)
    location = db.Column(db.String(64))
    website = db.Column(db.String(128))
    avatar_url = db.Column(db.String(200))  # 用户头像URL
    
    # 关系
    tasks = db.relationship('Task', backref='author', lazy='dynamic')
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

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def update_last_seen(self):
        self.last_seen = datetime.utcnow()
        db.session.commit()
    
    def __repr__(self):
        return '<User {}>'.format(self.username) 