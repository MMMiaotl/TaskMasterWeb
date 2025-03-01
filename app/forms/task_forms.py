from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, SubmitField, IntegerField, BooleanField, FloatField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional
from app.utils.constants import SERVICE_CHOICES

class TaskForm(FlaskForm):
    """任务创建和编辑表单"""
    title = StringField('任务标题', validators=[
        Optional(),
        Length(min=2, max=100, message='标题长度必须在2-100字符之间')
    ])
    
    service_category = SelectField('服务类别', 
        choices=SERVICE_CHOICES,
        validators=[DataRequired(message='请选择服务类别')]
    )
    
    description = TextAreaField('任务描述', validators=[
        Optional(),
        Length(min=10, max=1000, message='描述长度必须在10-1000字符之间')
    ])
    
    location = StringField('地点', validators=[
        Optional(),
        Length(max=100)
    ])
    
    deadline = DateField('截止日期', 
        format='%Y-%m-%d',
        validators=[DataRequired(message='请选择截止日期')]
    )
    
    budget = DecimalField('预算 (欧元)', 
        validators=[
            Optional(),
            NumberRange(min=1, message='预算必须大于0')
        ]
    )
    
    # 新增补充信息字段
    additional_info = TextAreaField('补充信息', 
        validators=[Optional(), Length(max=2000, message='补充信息不能超过2000字符')]
    )
    
    # 新增图片上传字段
    task_images = FileField('上传图片', 
        validators=[
            Optional(),
            FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '只允许上传图片文件!')
        ]
    )
    
    # 搬家服务特定字段
    moving_out_address = StringField('搬出地的邮编', validators=[
        Optional(),
        Length(min=6, max=6, message='例如: 1234AB')
    ])

    moving_in_address = StringField('搬入地的邮编', validators=[
        Optional(),
        Length(min=6, max=6, message='例如: 1234AB')
    ])

    moving_item_size = SelectField('物品大小', 
        choices=[('', '请选择物品大小'), ('small', '小型物品'), ('medium', '中型物品'), ('large', '大型物品')],
        validators=[Optional()]
    )
    
    moving_item_quantity = IntegerField('物品数量', 
        validators=[Optional(), NumberRange(min=1, message='物品数量必须大于0')]
    )
    
    moving_has_elevator = BooleanField('是否有电梯', default=False)
    
    moving_floor_number = IntegerField('楼层', 
        validators=[Optional(), NumberRange(min=0, message='楼层必须大于等于0')]
    )
    
    # 接送机特定字段
    pickup_flight_number = StringField('航班号', 
        validators=[Optional(), Length(max=20)]
    )
    
    pickup_passengers = IntegerField('乘客数量', 
        validators=[Optional(), NumberRange(min=1, message='乘客数量必须大于0')]
    )
    
    pickup_luggage_count = IntegerField('行李数量', 
        validators=[Optional(), NumberRange(min=0, message='行李数量必须大于等于0')]
    )
    
    pickup_is_arrival = RadioField('服务类型', 
        choices=[('1', '接机'), ('0', '送机')],
        validators=[Optional()]
    )
    
    # 装修维修特定字段
    repair_area = FloatField('面积（平方米）', 
        validators=[Optional(), NumberRange(min=0.1, message='面积必须大于0')]
    )
    
    repair_type = SelectField('维修类型', 
        choices=[
            ('', '请选择维修类型'), 
            ('water_electricity', '水电维修'), 
            ('wall', '墙面维修'), 
            ('floor', '地板维修'),
            ('furniture', '家具维修'),
            ('other', '其他维修')
        ],
        validators=[Optional()]
    )
    
    repair_materials_included = BooleanField('是否包含材料', default=False)
    
    # 法律咨询特定字段
    legal_case_type = SelectField('案件类型', 
        choices=[
            ('', '请选择案件类型'), 
            ('contract', '合同纠纷'), 
            ('immigration', '移民事务'), 
            ('business', '商业法律'),
            ('personal', '个人法律事务'),
            ('other', '其他法律事务')
        ],
        validators=[Optional()]
    )
    
    legal_urgency = SelectField('紧急程度', 
        choices=[
            ('', '请选择紧急程度'), 
            ('low', '不紧急'), 
            ('medium', '一般'), 
            ('high', '紧急')
        ],
        validators=[Optional()]
    )
    
    legal_documents_ready = BooleanField('文件是否准备好', default=False)
    
    # 留学咨询特定字段
    education_target_country = SelectField('目标国家', 
        choices=[
            ('', '请选择目标国家'), 
            ('usa', '美国'), 
            ('uk', '英国'), 
            ('canada', '加拿大'),
            ('australia', '澳大利亚'),
            ('germany', '德国'),
            ('france', '法国'),
            ('other', '其他国家')
        ],
        validators=[Optional()]
    )
    
    education_study_level = SelectField('学习阶段', 
        choices=[
            ('', '请选择学习阶段'), 
            ('bachelor', '本科'), 
            ('master', '硕士'), 
            ('phd', '博士'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    education_field = SelectField('学习领域', 
        choices=[
            ('', '请选择学习领域'), 
            ('business', '商科'), 
            ('engineering', '工程'), 
            ('science', '理科'),
            ('arts', '文科'),
            ('medicine', '医学'),
            ('law', '法律'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    # 维修服务特定字段
    repair_service_type = SelectField('维修类型', 
        choices=[
            ('', '请选择维修类型'), 
            ('electronics', '电子设备'), 
            ('appliances', '家用电器'), 
            ('furniture', '家具'),
            ('plumbing', '水管'),
            ('electrical', '电路'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    repair_service_item_age = SelectField('物品年龄', 
        choices=[
            ('', '请选择物品年龄'), 
            ('less_than_1', '不到1年'), 
            ('1_to_3', '1-3年'), 
            ('3_to_5', '3-5年'),
            ('more_than_5', '5年以上'),
            ('unknown', '不确定')
        ],
        validators=[Optional()]
    )
    
    repair_service_brand_model = StringField('品牌和型号', 
        validators=[Optional(), Length(max=100)]
    )
    
    repair_service_has_warranty = BooleanField('是否在保修期内', default=False)
    
    # 其他商业服务特定字段
    other_business_service_type = SelectField('服务类型', 
        choices=[
            ('', '请选择服务类型'), 
            ('marketing', '市场营销'), 
            ('design', '设计服务'), 
            ('translation', '翻译服务'),
            ('accounting', '会计服务'),
            ('it_support', 'IT支持'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    other_business_project_scale = SelectField('项目规模', 
        choices=[
            ('', '请选择项目规模'), 
            ('small', '小型'), 
            ('medium', '中型'), 
            ('large', '大型')
        ],
        validators=[Optional()]
    )
    
    other_business_duration = SelectField('预计时长', 
        choices=[
            ('', '请选择预计时长'), 
            ('one_time', '一次性服务'), 
            ('short_term', '短期（1-3个月）'), 
            ('long_term', '长期（3个月以上）')
        ],
        validators=[Optional()]
    )
    
    submit = SubmitField('发布任务') 