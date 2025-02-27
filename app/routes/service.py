from flask import Blueprint, render_template, current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from app.models import Task, ServiceView
from sqlalchemy import or_
from app.utils.constants import SERVICE_CATEGORIES
from app import db
from datetime import datetime

# 修改蓝图名称
service_bp = Blueprint('service', __name__, url_prefix='/service')

# 获取服务对应的图标
def get_icon_for_service(service_id):
    # 为每个服务ID定义对应的图标
    icon_mapping = {
        'moving': 'fa-truck',
        'pickup': 'fa-plane-arrival',
        'driving': 'fa-car',
        'repair': 'fa-tools',
        'housing': 'fa-home',
        'company': 'fa-building',
        'translation': 'fa-file-alt',
        'education': 'fa-graduation-cap',
        'accounting': 'fa-calculator',
        'legal': 'fa-gavel',
        'investment': 'fa-chart-line',
        'shop': 'fa-store'
    }
    return icon_mapping.get(service_id, 'fa-question')  # 默认图标

# 服务详情数据
def get_service_details():
    service_details = {}
    for category in SERVICE_CATEGORIES:
        for subcategory in category['subcategories']:
            service_id = subcategory[0]
            service_details[service_id] = {
                'id': service_id,
                'name': subcategory[1],
                'description': f"专业的{subcategory[1]}服务",
                'icon': get_icon_for_service(service_id)
            }
    return service_details

@service_bp.route('/<category>/<service_id>')
def service_page(category, service_id):
    try:
        # 记录浏览量
        ServiceView.increment_view(category, service_id)
        
        # 获取服务数据
        services = get_services_from_categories()
        service_details = get_service_details()
        
        # 获取当前服务信息
        current_service = service_details.get(service_id)
        if not current_service:
            current_app.logger.error(f"Service not found: {service_id}")
            return render_template('errors/404.html'), 404
            
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

@service_bp.route('/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 1:
        return jsonify([])
    
    # 从数据库中查询相关任务
    suggestions = Task.query.filter(
        or_(
            Task.title.ilike(f'%{query}%'),
            Task.description.ilike(f'%{query}%')
        )
    ).limit(5).all()
    
    # 格式化建议结果
    results = [{
        'id': task.id,
        'title': task.title,
        'description': task.description[:100] + '...' if len(task.description) > 100 else task.description,
        'url': url_for('task.task_detail', task_id=task.id)
    } for task in suggestions]
    
    return jsonify(results)

# 服务分类数据 - 使用常量文件中的定义
def get_services_from_categories():
    services = {}
    for category in SERVICE_CATEGORIES:
        services[category['id']] = {
            'name': category['name'],
            'services': [
                {
                    'id': subcategory[0],
                    'name': subcategory[1],
                    'icon': get_icon_for_service(subcategory[0])
                }
                for subcategory in category['subcategories']
            ]
        }
    return services 