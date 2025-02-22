from app import db
from datetime import datetime

class Review(db.Model):
    __tablename__ = 'reviews'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # 外键关系
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'), nullable=False) 
    
    # 评价类型（'poster' 或 'executor'）
    role = db.Column(db.String(20), nullable=False)
    
    # 关系定义
    reviewer = db.relationship('User', foreign_keys=[reviewer_id],
                             backref=db.backref('reviews_given', lazy='dynamic'))
    reviewee = db.relationship('User', foreign_keys=[reviewee_id],
                             backref=db.backref('reviews_received', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        return f'<Review {self.id}>' 