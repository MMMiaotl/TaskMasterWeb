from flask import Blueprint, render_template, current_app
from flask_login import current_user

# 修改蓝图名称
service_bp = Blueprint('service', __name__, url_prefix='/service')

# 服务分类数据
SERVICES = {
    'daily': {
        'name': '日常生活',
        'items': [
            {'id': 'moving', 'name': '搬家服务', 'icon': 'fa-truck'},
            {'id': 'pickup', 'name': '接送机', 'icon': 'fa-plane-arrival'},
            {'id': 'driving', 'name': '代驾服务', 'icon': 'fa-car'},
            {'id': 'repair', 'name': '装修维修', 'icon': 'fa-tools'}
        ]
    },
    'professional': {
        'name': '专业服务',
        'items': [
            {'id': 'housing', 'name': '房产中介', 'icon': 'fa-home'},
            {'id': 'company', 'name': '公司注册', 'icon': 'fa-building'},
            {'id': 'translation', 'name': '文件翻译', 'icon': 'fa-file-alt'},
            {'id': 'education', 'name': '留学咨询', 'icon': 'fa-graduation-cap'}
        ]
    },
    'business': {
        'name': '商业服务',
        'items': [
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
        # 添加调试日志
        current_app.logger.info(f"Accessing service page with category: {category}, service_id: {service_id}")
        
        # 获取当前服务的信息
        service_info = None
        category_info = SERVICES.get(category)
        
        # 打印调试信息
        current_app.logger.info(f"Category info: {category_info}")
        
        if not category_info:
            current_app.logger.error(f"Category not found: {category}")
            return render_template('errors/404.html'), 404
            
        for service_item in category_info['items']:
            if service_item['id'] == service_id:
                service_info = service_item
                break
        
        # 打印调试信息
        current_app.logger.info(f"Service info: {service_info}")
        
        if not service_info:
            current_app.logger.error(f"Service not found: {service_id} in category {category}")
            return render_template('errors/404.html'), 404
        
        # 这里应该从数据库获取该服务类型的任务列表
        tasks = [
            {
                'id': 1,
                'title': '2房1厅搬家服务',
                'price': 500,
                'location': '市中心',
                'description': '需要搬家公司帮忙搬运家具和电器，约3小时工作量',
                'created_at': '2024-03-15',
                'user': {
                    'username': '张先生',
                    'avatar_url': '/static/img/default-avatar.png'
                }
            },
            {
                'id': 2,
                'title': '单身公寓搬迁',
                'price': 300,
                'location': '郊区',
                'description': '一个人的行李，主要是衣物和生活用品，需要搬运到新住处',
                'created_at': '2024-03-14',
                'user': {
                    'username': '李女士',
                    'avatar_url': '/static/img/default-avatar.png'
                }
            }
        ]
        
        # 打印模板渲染信息
        current_app.logger.info(f"Rendering template with services={SERVICES}, current_category={category}, current_service={service_info}")
        
        try:
            return render_template('service/service_page.html',
                                services=SERVICES,
                                current_category=category,
                                current_service=service_info,
                                tasks=tasks)
        except Exception as template_error:
            current_app.logger.error(f"Template rendering error: {str(template_error)}")
            raise
                            
    except Exception as e:
        current_app.logger.error(f"Error in service_page: {str(e)}")
        return render_template('errors/404.html'), 404 