from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, SubmitField, IntegerField, BooleanField, FloatField, RadioField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Regexp
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
    
    # 时间类型选择
    time_preference = RadioField('时间偏好',
        choices=[
            ('specific_date', '我有个明确的日期'),
            ('date_range', '我有个期望的日期范围'),
            ('anytime', '任何时间都可以'),
            ('not_sure', '不确定')
        ],
        validators=[DataRequired(message='请选择时间偏好')]
    )
    
    deadline = DateField('截止日期', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    
    # 日期范围字段
    start_date = DateField('开始日期',
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    
    end_date = DateField('结束日期',
        format='%Y-%m-%d',
        validators=[Optional()]
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
        Length(min=6, max=6, message='邮编必须是6位字符'),
        Regexp(r'^[0-9]{4}[A-Za-z]{2}$', message='邮编格式必须是4位数字+2位字母，例如: 1234AB')
    ])

    moving_in_address = StringField('搬入地的邮编', validators=[
        Optional(),
        Length(min=6, max=6, message='邮编必须是6位字符'),
        Regexp(r'^[0-9]{4}[A-Za-z]{2}$', message='邮编格式必须是4位数字+2位字母，例如: 1234AB')
    ])

    # 新增房屋类型字段
    moving_out_house_type = SelectField('搬出地点房屋类型', 
        choices=[
            ('', '请选择房屋类型'), 
            ('apartment', '公寓'), 
            ('house', '联排别墅'), 
            ('commercial', '商铺'),
            ('warehouse', '仓库'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    moving_in_house_type = SelectField('搬入地点房屋类型', 
        choices=[
            ('', '请选择房屋类型'), 
            ('apartment', '公寓'), 
            ('house', '联排别墅'), 
            ('commercial', '商铺'),
            ('warehouse', '仓库'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    # 修改电梯和楼层字段
    moving_out_has_elevator = BooleanField('搬出地点是否有电梯', default=False)
    moving_in_has_elevator = BooleanField('搬入地点是否有电梯', default=False)
    
    moving_out_floor_number = IntegerField('搬出地点楼层', 
        validators=[Optional(), NumberRange(min=0, message='楼层必须大于等于0')]
    )
    
    moving_in_floor_number = IntegerField('搬入地点楼层', 
        validators=[Optional(), NumberRange(min=0, message='楼层必须大于等于0')]
    )
    
    # 修改物品数量为范围选择
    moving_item_quantity_range = SelectField('物品数量范围', 
        choices=[
            ('', '请选择物品数量范围'), 
            ('1-5', '1-5箱'), 
            ('6-15', '6-15箱'), 
            ('16-30', '16-30箱'),
            ('30+', '30箱以上')
        ],
        validators=[Optional()]
    )
    
    # 特殊物品字段
    moving_has_large_furniture = BooleanField('有大型家具', default=False)
    moving_has_appliances = BooleanField('有家用电器', default=False)
    moving_has_fragile_items = BooleanField('有易碎物品', default=False)
    moving_has_piano = BooleanField('有钢琴或其他乐器', default=False)
    moving_other_special_items = StringField('其他特殊物品', validators=[Optional(), Length(max=200)])
    
    # 搬家时间字段
    moving_preferred_date = DateField('首选日期', 
        format='%Y-%m-%d',
        validators=[Optional()]
    )
    
    moving_preferred_time = SelectField('首选时间段', 
        choices=[
            ('', '请选择时间段'), 
            ('morning', '上午 (8:00-12:00)'), 
            ('afternoon', '下午 (12:00-17:00)'), 
            ('evening', '晚上 (17:00-21:00)')
        ],
        validators=[Optional()]
    )
    
    moving_is_flexible = BooleanField('时间灵活', default=True)
    
    # 额外服务字段
    moving_need_packing = BooleanField('需要打包服务', default=False)
    moving_need_unpacking = BooleanField('需要拆包服务', default=False)
    moving_need_disposal = BooleanField('需要废物处理', default=False)
    moving_need_storage = BooleanField('需要临时存储', default=False)
    
    # 保留原有字段但不再使用
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
    
    # 新增装修翻新工作内容多选字段
    repair_work_painting = BooleanField('刷漆', default=False)
    repair_work_plastering = BooleanField('批灰', default=False)
    repair_work_flooring = BooleanField('铺地板', default=False)
    repair_work_plumbing = BooleanField('改水电', default=False)
    repair_work_bathroom = BooleanField('浴室', default=False)
    repair_work_toilet = BooleanField('厕所', default=False)
    repair_work_kitchen = BooleanField('厨房', default=False)
    repair_work_garden = BooleanField('花园', default=False)
    repair_work_extension = BooleanField('扩建', default=False)
    repair_work_other = StringField('其他工作', validators=[Optional(), Length(max=200)])
    
    # 新增装修翻新地址邮编字段
    repair_address = StringField('地址邮编', validators=[
        Optional(),
        Length(min=6, max=6, message='邮编必须是6位字符'),
        Regexp(r'^[0-9]{4}[A-Za-z]{2}$', message='邮编格式必须是4位数字+2位字母，例如: 1234AB')
    ])
    
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
    
    # 检车服务特定字段
    car_brand = SelectField('汽车品牌', 
        choices=[
            ('', '请选择汽车品牌'),
            ('audi', '奥迪 (Audi)'),
            ('bmw', '宝马 (BMW)'),
            ('mercedes', '奔驰 (Mercedes-Benz)'),
            ('volkswagen', '大众 (Volkswagen)'),
            ('toyota', '丰田 (Toyota)'),
            ('honda', '本田 (Honda)'),
            ('ford', '福特 (Ford)'),
            ('nissan', '日产 (Nissan)'),
            ('hyundai', '现代 (Hyundai)'),
            ('kia', '起亚 (Kia)'),
            ('peugeot', '标致 (Peugeot)'),
            ('renault', '雷诺 (Renault)'),
            ('citroen', '雪铁龙 (Citroën)'),
            ('opel', '欧宝 (Opel)'),
            ('volvo', '沃尔沃 (Volvo)'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    car_model = StringField('车型', validators=[
        Optional(),
        Length(max=50, message='车型名称不能超过50个字符')
    ])
    
    car_year = IntegerField('车辆年份', validators=[
        Optional(),
        NumberRange(min=1900, max=2100, message='请输入有效的车辆年份')
    ])
    
    car_fuel_type = SelectField('燃料类型',
        choices=[
            ('', '请选择燃料类型'),
            ('gasoline', '汽油'),
            ('diesel', '柴油'),
            ('hybrid', '混合动力'),
            ('electric', '纯电动'),
            ('lpg', 'LPG液化石油气'),
            ('cng', 'CNG压缩天然气'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    car_license_plate = StringField('车牌号码', validators=[
        Optional(),
        Length(max=20, message='车牌号码不能超过20个字符')
    ])
    
    car_inspection_type = SelectField('检车类型',
        choices=[
            ('', '请选择检车类型'),
            ('regular', '常规年检'),
            ('pre_purchase', '二手车购买前检查'),
            ('emission', '尾气排放检测'),
            ('safety', '安全检查'),
            ('damage', '事故后检查'),
            ('other', '其他')
        ],
        validators=[Optional()]
    )
    
    car_has_previous_issues = BooleanField('车辆之前是否有问题')
    
    car_previous_issues = TextAreaField('之前的问题描述', validators=[
        Optional(),
        Length(max=500, message='问题描述不能超过500个字符')
    ])
    
    submit = SubmitField('发布任务') 