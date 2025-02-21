from app import db
from datetime import datetime

class Rating(db.Model):
    __tablename__ = 'rating'
    
    id = db.Column(db.Integer, primary_key=True)
    rater_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 评分者
    rated_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 被评分者
    score = db.Column(db.Float, nullable=False)  # 评分（1-5）
    comment = db.Column(db.Text)  # 评分评论
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    #task_id = db.Column(db.Integer, db.ForeignKey('task.id'))  # 关联的任务（可选） 