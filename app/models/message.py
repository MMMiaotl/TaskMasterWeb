from app import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, 
        index=True, 
        default=datetime.utcnow,
        nullable=False
    )
    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    is_read = db.Column(db.Boolean, default=False)

    task = db.relationship('Task', back_populates='messages')

    def __repr__(self):
        return f'<Message {self.id}>' 