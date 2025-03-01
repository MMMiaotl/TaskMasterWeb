# 服务类别定义
SERVICE_CATEGORIES = [
    {
        'id': 'daily',
        'name': '日常生活',
        'icon': 'fas fa-home',
        'subcategories': [
            ('moving', '搬家服务'),
            ('pickup', '接送机'),
            ('driving', '代驾服务'),
            ('repair', '装修翻新')
        ]
    },
    {
        'id': 'professional',
        'name': '专业服务',
        'icon': 'fas fa-briefcase',
        'subcategories': [
            ('housing', '房产中介'),
            ('company', '公司注册'),
            ('translation', '文件翻译'),
            ('education', '留学咨询')
        ]
    },
    {
        'id': 'business',
        'name': '商业服务',
        'icon': 'fas fa-chart-line',
        'subcategories': [
            ('accounting', '会计税务'),
            ('legal', '法律咨询'),
            ('repair_service', '维修服务'),
            ('other_business', '其他商业服务')
        ]
    }
]

# 将子类别展平为选项列表，用于表单选择
SERVICE_CHOICES = [('', '请选择服务类别')]
for category in SERVICE_CATEGORIES:
    # 添加主类别作为选项组标题
    SERVICE_CHOICES.append((category['id'], f"== {category['name']} =="))
    # 添加该类别下的所有子类别
    for subcategory in category['subcategories']:
        SERVICE_CHOICES.append(
            (f"{category['id']}.{subcategory[0]}", 
             f"{subcategory[1]}")
        ) 