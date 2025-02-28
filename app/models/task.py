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
    executor_id = db.Column(db.Integer, db.ForeignKey('user.id', name='fk_task_executor'), nullable=True)
    executor = db.relationship('User', foreign_keys=[executor_id])
    view_count = db.Column(db.Integer, default=0)
    featured = db.Column(db.Boolean, default=False)

    # 服务类别特定字段
    # 搬家服务特定字段
    moving_item_size = db.Column(db.String(50))  # 物品大小：小型/中型/大型
    moving_item_quantity = db.Column(db.Integer)  # 物品数量
    moving_has_elevator = db.Column(db.Boolean)  # 是否有电梯
    moving_floor_number = db.Column(db.Integer)  # 楼层
    
    # 接送机特定字段
    pickup_flight_number = db.Column(db.String(20))  # 航班号
    pickup_passengers = db.Column(db.Integer)  # 乘客数量
    pickup_luggage_count = db.Column(db.Integer)  # 行李数量
    pickup_is_arrival = db.Column(db.Boolean)  # 是接机还是送机
    
    # 装修维修特定字段
    repair_area = db.Column(db.Float)  # 面积（平方米）
    repair_type = db.Column(db.String(50))  # 维修类型：水电/墙面/地板等
    repair_materials_included = db.Column(db.Boolean)  # 是否包含材料
    
    # 法律咨询特定字段
    legal_case_type = db.Column(db.String(50))  # 案件类型
    legal_urgency = db.Column(db.String(20))  # 紧急程度
    legal_documents_ready = db.Column(db.Boolean)  # 文件是否准备好
    
    # 留学咨询特定字段
    education_target_country = db.Column(db.String(50))  # 目标国家
    education_study_level = db.Column(db.String(30))  # 学习阶段：本科/硕士/博士
    education_field = db.Column(db.String(50))  # 学习领域
    
    # 定义与消息的关系
    messages = db.relationship(
        'Message', 
        back_populates='task',
        cascade='all, delete-orphan'
    )

    def __init__(self, **kwargs):
        super(Task, self).__init__(**kwargs)
        if self.service_category:
            try:
                main_cat, sub_cat = self.service_category.split('.')
                self.service_main_category = main_cat
                self.service_sub_category = sub_cat
            except ValueError:
                # 如果格式不正确，可以记录日志或设置默认值
                self.service_main_category = self.service_category
                self.service_sub_category = None

    def __repr__(self):
        return f'<Task {self.title}>' 

    def get_status_name(self):
        return self.STATUS_CHOICES.get(self.status, '未知状态') 