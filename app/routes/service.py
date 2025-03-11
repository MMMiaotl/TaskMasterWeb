from flask import Blueprint, render_template, current_app, request, jsonify, url_for, flash, redirect
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
        'car_inspection': 'fa-car-alt',  # 检车服务图标
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
        
        # 权限检查
        access_granted = True
        error_message = ""
        
        if current_user.is_authenticated:
            # 如果不是专业人士且不是管理员，显示权限错误
            if not current_user.is_professional and not current_user.is_admin():
                access_granted = False
                error_message = '普通用户无权访问服务子类别页面'
                flash(error_message, 'warning')
            
            # 如果是专业人士，检查是否注册了该服务子类别
            elif current_user.is_professional:
                category_id = f"{category}.{service_id}"
                if not current_user.has_category(category_id) and not current_user.is_admin():
                    access_granted = False
                    error_message = '您没有注册该服务子类别，无法访问相关任务'
                    flash(error_message, 'warning')
        else:
            # 未登录用户无权访问
            access_granted = False
            error_message = '请先登录后再访问服务详情页'
            flash(error_message, 'info')
        
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
        if date_sort == 'recent':
            query = query.order_by(Task.created_at.desc())
        elif date_sort == 'oldest':
            query = query.order_by(Task.created_at.asc())
        elif date_sort == 'deadline':
            # 按截止日期排序，没有截止日期的排在最后
            query = query.order_by(
                Task.deadline.is_(None),
                Task.deadline.asc()
            )
        else:
            # 默认按最近发布排序
            query = query.order_by(Task.created_at.desc())
        
        # 应用位置过滤
        if location_filter:
            query = query.filter(Task.location.ilike(f'%{location_filter}%'))
        
        # 执行查询
        tasks = query.all()
        
        # 获取此类别的热门搜索词
        # 这部分可以根据用户行为或历史搜索来动态生成
        popular_searches = ["搬家", "翻译", "面试辅导", "代购"]
        
        # 返回结果
        return render_template(
            'service/service_page.html',
            category=category,
            service=current_service,
            tasks=tasks if access_granted else [],
            price_sort=price_sort,
            date_sort=date_sort,
            location_filter=location_filter,
            popular_searches=popular_searches,
            access_denied=not access_granted,
            error_message=error_message
        )
        
    except Exception as e:
        current_app.logger.error(f"访问服务页面时出错: {str(e)}")
        flash('加载服务页面时出错', 'danger')
        return redirect(url_for('main.index'))

@service_bp.route('/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip()
    if not query or len(query) < 1:
        return jsonify([])
    
    # 从数据库中查询相关任务，排除已取消的任务
    suggestions = Task.query.filter(
        or_(
            Task.title.ilike(f'%{query}%'),
            Task.description.ilike(f'%{query}%')
        )
    ).filter(Task.status != 4).limit(5).all()
    
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