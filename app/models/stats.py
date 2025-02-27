from app import db
from datetime import datetime

class ServiceView(db.Model):
    __tablename__ = 'service_views'
    
    id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    user = db.relationship('User', backref='service_views')

class TaskView(db.Model):
    __tablename__ = 'task_views'
    
    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    task = db.relationship('Task', backref='views')
    user = db.relationship('User', backref='task_views') 