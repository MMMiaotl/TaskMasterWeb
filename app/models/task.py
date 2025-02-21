from app import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = 'tasks'
    
    STATUS_CHOICES = {
        0: '等待接单',
        1: '等待执行',
        2: '任务完成',
        3: '付款完成'
    }
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    service_category = db.Column(db.String(50), nullable=False)  # 格式: "category.subcategory"
    service_main_category = db.Column(db.String(30))  # 主类别，用于快速筛选
    service_sub_category = db.Column(db.String(30))  # 子类别
    location = db.Column(db.String(100), nullable=False)
    deadline = db.Column(db.DateTime, nullable=False)
    budget = db.Column(db.Float, nullable=False)
    status = db.Column(db.Integer, default=0)  # 0: 等待接单, 1: 已接单, 2: 进行中, 3: 已完成
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    

    # 定义与消息的关系
    messages = db.relationship(
        'Message', 
        back_populates='task',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        if self.service_category:
            main_cat, sub_cat = self.service_category.split('.')
            self.service_main_category = main_cat
            self.service_sub_category = sub_cat

    def __repr__(self):
        return f'<Task {self.title}>' 