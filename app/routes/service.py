from flask import Blueprint, render_template, current_app
from flask_login import current_user
from app.models import Task
from sqlalchemy import or_

# 修改蓝图名称
service_bp = Blueprint('service', __name__, url_prefix='/service')

# 服务分类数据
SERVICES = {
    'daily': {
        'name': '日常生活',
        'services': [
            {'id': 'moving', 'name': '搬家服务', 'icon': 'fa-truck'},
            {'id': 'pickup', 'name': '接送机', 'icon': 'fa-plane-arrival'},
            {'id': 'driving', 'name': '代驾服务', 'icon': 'fa-car'},
            {'id': 'repair', 'name': '装修维修', 'icon': 'fa-tools'}
        ]
    },
    'professional': {
        'name': '专业服务',
        'services': [
            {'id': 'housing', 'name': '房产中介', 'icon': 'fa-home'},
            {'id': 'company', 'name': '公司注册', 'icon': 'fa-building'},
            {'id': 'translation', 'name': '文件翻译', 'icon': 'fa-file-alt'},
            {'id': 'education', 'name': '留学咨询', 'icon': 'fa-graduation-cap'}
        ]
    },
    'business': {
        'name': '商业服务',
        'services': [
            {'id': 'accounting', 'name': '会计税务', 'icon': 'fa-calculator'},
            {'id': 'legal', 'name': '法律咨询', 'icon': 'fa-gavel'},
            {'id': 'investment', 'name': '投资理财', 'icon': 'fa-chart-line'},
            {'id': 'shop', 'name': '商铺转让', 'icon': 'fa-store'}
        ]
    }
}

@service_bp.route('/<category>/<service_id>')
def service_page(category, service_id):
    try:
        # 查询与服务类别相关的任务
        tasks = Task.query.filter(Task.service_category == f"{category}.{service_id}").all()
        
        # 获取服务信息（假设您有一个服务信息字典或模型）
        service_info = {
            'id': service_id,
            'name': '搬家服务'  # 这里可以根据实际情况动态获取
        }
        
        return render_template('service/service_page.html',
                               services=SERVICES,
                               current_category=category,
                               current_service=service_info,
                               tasks=tasks)
    except Exception as e:
        current_app.logger.error(f"Error in service_page: {str(e)}")
        return render_template('errors/404.html'), 404 