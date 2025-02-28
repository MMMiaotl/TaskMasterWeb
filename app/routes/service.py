from flask import Blueprint, render_template, current_app, request, jsonify, url_for
from flask_login import current_user, login_required
from app.models import Task, ServiceView
from sqlalchemy import or_
from app.utils.constants import SERVICE_CATEGORIES
from app import db
from datetime import datetime, timedelta

# 修改蓝图名称
service_bp = Blueprint('service', __name__)

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
        # 添加详细的请求日志
        current_app.logger.info(f"访问服务页面: URL={request.path}, 类别={category}, 服务ID={service_id}")
        current_app.logger.info(f"请求方法: {request.method}, 请求参数: {dict(request.args)}")
        
        # 获取服务详情
        service_details = get_service_details()
        if service_id not in service_details:
            current_app.logger.error(f"服务ID不存在: {service_id}")
            return render_template('errors/404.html'), 404
        
        current_service = service_details[service_id]
        
        # 记录服务访问
        ServiceView.increment_view(category, service_id)
        
        # 获取过滤器参数
        price_sort = request.args.get('price_sort', '')
        date_sort = request.args.get('date_sort', '')
        location_filter = request.args.get('location', '')
        
        # 构建基本查询
        query = Task.query.filter_by(
            service_main_category=category,
            service_sub_category=service_id
        )
        
        # 应用价格排序
        if price_sort == 'asc':
            query = query.order_by(Task.budget.asc())
        elif price_sort == 'desc':
            query = query.order_by(Task.budget.desc())
        
        # 应用日期排序/过滤
        now = datetime.utcnow()
        
        if date_sort == 'newest':
            query = query.order_by(Task.created_at.desc())
        elif date_sort == 'last_week':
            one_week_ago = now - timedelta(days=7)
            query = query.filter(Task.created_at >= one_week_ago).order_by(Task.created_at.desc())
        elif date_sort == 'last_month':
            one_month_ago = now - timedelta(days=30)
            query = query.filter(Task.created_at >= one_month_ago).order_by(Task.created_at.desc())
        else:
            # 默认按创建时间降序排序
            query = query.order_by(Task.created_at.desc())
        
        # 应用位置过滤
        if location_filter and location_filter != 'all':
            if location_filter == 'city_center':
                query = query.filter(Task.location.ilike('%市中心%'))
            elif location_filter == 'suburbs':
                query = query.filter(Task.location.ilike('%郊区%'))
        
        # 执行查询并限制结果数量
        tasks = query.limit(10).all()
        
        # 获取所有服务分类数据
        services = get_services_from_categories()
        
        # 渲染服务页面模板
        return render_template(
            'service/service_page.html',
            current_service=current_service,
            category=category,
            service_id=service_id,
            category_name=next((c['name'] for c in SERVICE_CATEGORIES if c['id'] == category), '未知分类'),
            services=services,
            tasks=tasks,
            debug=False,  # 关闭调试信息显示
            request=request  # 传递请求对象以便在模板中访问参数
        )
        
    except Exception as e:
        current_app.logger.error(f"服务页面错误: {str(e)}")
        import traceback
        current_app.logger.error(f"详细错误堆栈: {traceback.format_exc()}")
        return f"错误: {str(e)}", 500

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

# 添加一个简单的调试路由
@service_bp.route('/debug')
def debug_route():
    """简单的调试路由，用于测试服务蓝图是否正确注册"""
    routes_info = {
        'blueprint_name': service_bp.name,
        'url_prefix': service_bp.url_prefix,
        'routes': [str(rule) for rule in current_app.url_map.iter_rules() 
                  if rule.endpoint.startswith('service.')],
        'service_details': list(get_service_details().keys()),
        'categories': [category['id'] for category in SERVICE_CATEGORIES]
    }
    return jsonify(routes_info)

@service_bp.route('/')
def service_index():
    """服务首页，展示所有服务类别，并支持搜索"""
    services = get_services_from_categories()
    search_query = request.args.get('q', '').strip()
    search_results = []
    
    # 如果有搜索查询，筛选匹配的服务
    if search_query:
        query_lower = search_query.lower()
        for category_id, category_data in services.items():
            category_name = category_data['name']
            
            # 检查类别名称是否匹配
            category_match = query_lower in category_name.lower()
            
            # 筛选匹配的服务
            matching_services = []
            for service in category_data['services']:
                if query_lower in service['name'].lower() or category_match:
                    # 复制服务信息并添加类别信息
                    service_info = service.copy()
                    service_info['category_id'] = category_id
                    service_info['category_name'] = category_name
                    matching_services.append(service_info)
            
            # 如果有匹配的服务，添加到结果中
            if matching_services:
                search_results.extend(matching_services)
        
        # 按相关性排序：优先显示以查询开头的结果
        search_results.sort(key=lambda x: (0 if x['name'].lower().startswith(query_lower) else 1, x['name']))
    
    return render_template(
        'service/service_index.html', 
        services=services, 
        search_query=search_query,
        search_results=search_results
    )

@service_bp.route('/ajax_tasks/<category>/<service_id>')
def ajax_tasks(category, service_id):
    try:
        # 获取过滤器参数
        price_sort = request.args.get('price_sort', '')
        date_sort = request.args.get('date_sort', '')
        location_filter = request.args.get('location', '')
        
        # 构建基本查询
        query = Task.query.filter_by(
            service_main_category=category,
            service_sub_category=service_id
        )
        
        # 应用价格排序
        if price_sort == 'asc':
            query = query.order_by(Task.budget.asc())
        elif price_sort == 'desc':
            query = query.order_by(Task.budget.desc())
        
        # 应用日期排序/过滤
        now = datetime.utcnow()
        
        if date_sort == 'newest':
            query = query.order_by(Task.created_at.desc())
        elif date_sort == 'last_week':
            one_week_ago = now - timedelta(days=7)
            query = query.filter(Task.created_at >= one_week_ago).order_by(Task.created_at.desc())
        elif date_sort == 'last_month':
            one_month_ago = now - timedelta(days=30)
            query = query.filter(Task.created_at >= one_month_ago).order_by(Task.created_at.desc())
        else:
            # 默认按创建时间降序排序
            query = query.order_by(Task.created_at.desc())
        
        # 应用位置过滤
        if location_filter and location_filter != 'all':
            if location_filter == 'city_center':
                query = query.filter(Task.location.ilike('%市中心%'))
            elif location_filter == 'suburbs':
                query = query.filter(Task.location.ilike('%郊区%'))
        
        # 执行查询并限制结果数量
        tasks = query.limit(10).all()
        
        # 只渲染任务列表部分
        return render_template(
            'service/task_list_partial.html',
            tasks=tasks
        )
        
    except Exception as e:
        current_app.logger.error(f"AJAX任务列表错误: {str(e)}")
        import traceback
        current_app.logger.error(f"详细错误堆栈: {traceback.format_exc()}")
        return f"错误: {str(e)}", 500 