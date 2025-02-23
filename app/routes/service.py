from flask import Blueprint, render_template, current_app
from flask_login import current_user, login_required
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
        # 获取当前服务信息
        current_service = get_service_by_id(service_id)
        if not current_service:
            current_app.logger.error(f"Service not found: {service_id}")
            return render_template('errors/404.html'), 404
            
        # 获取所有服务分类
        services = get_all_services()
        
        # 查询相关任务
        tasks = Task.query.filter(Task.service_category == f"{category}.{service_id}").all()
        
        return render_template('service/service_page.html',
                             current_service=current_service,
                             services=services,
                             tasks=tasks,
                             category=category,
                             service_id=service_id)
    except Exception as e:
        current_app.logger.error(f"Error in service_page: {str(e)}")
        return render_template('errors/404.html'), 404

def get_service_by_id(service_id):
    # 这里实现从数据库或配置中获取服务信息的逻辑
    # 示例使用硬编码数据
    services = {
        'moving': {
            'id': 'moving',
            'name': 'Moving Help',
            'description': 'Professional moving services',
            'icon': 'fa-truck'
        },
        'pickup': {
            'id': 'pickup',
            'name': 'Airport Pickup',
            'description': 'Reliable airport pickup services',
            'icon': 'fa-plane-arrival'
        },
        'driving': {
            'id': 'driving',
            'name': 'Driving Service',
            'description': 'Professional driving services',
            'icon': 'fa-car'
        },
        'repair': {
            'id': 'repair',
            'name': 'Home Repair',
            'description': 'Professional home repair services',
            'icon': 'fa-tools'
        },
        'housing': {
            'id': 'housing',
            'name': 'Real Estate',
            'description': 'Professional real estate services',
            'icon': 'fa-home'
        },
        'company': {
            'id': 'company',
            'name': 'Company Setup',
            'description': 'Professional company setup services',
            'icon': 'fa-building'
        },
        'translation': {
            'id': 'translation',
            'name': 'Translation',
            'description': 'Professional translation services',
            'icon': 'fa-file-alt'
        },
        'education': {
            'id': 'education',
            'name': 'Study Abroad',
            'description': 'Professional study abroad services',
            'icon': 'fa-graduation-cap'
        },
        'accounting': {
            'id': 'accounting',
            'name': 'Accounting',
            'description': 'Professional accounting services',
            'icon': 'fa-calculator'
        },
        'legal': {
            'id': 'legal',
            'name': 'Legal Advice',
            'description': 'Professional legal advice services',
            'icon': 'fa-gavel'
        },
        'investment': {
            'id': 'investment',
            'name': 'Investment',
            'description': 'Professional investment services',
            'icon': 'fa-chart-line'
        },
        'shop': {
            'id': 'shop',
            'name': 'Shop Transfer',
            'description': 'Professional shop transfer services',
            'icon': 'fa-store'
        }
    }
    return services.get(service_id)

def get_all_services():
    # 返回所有服务分类
    return SERVICES  # 使用之前定义的SERVICES常量 