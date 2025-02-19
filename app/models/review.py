from app import db
from datetime import datetime, timezone

class Review(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    reviewee_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    task_id = db.Column(db.Integer, db.ForeignKey('task.id'))
    role = db.Column(db.String(20))  # 'poster' or 'executor'

    # 关系
    reviewer = db.relationship('User', foreign_keys=[reviewer_id],
                             backref=db.backref('reviews_given', lazy='dynamic'))
    reviewee = db.relationship('User', foreign_keys=[reviewee_id],
                             backref=db.backref('reviews_received', lazy='dynamic'))
    task = db.relationship('Task', backref=db.backref('reviews', lazy='dynamic'))

    def __repr__(self):
        return f'<Review {self.id}>' 