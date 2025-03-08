from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, jsonify
from app.models import Task, ServiceView
from sqlalchemy import or_
from flask_login import current_user
import time
from app.utils.constants import SERVICE_CATEGORIES
from app.routes.service import get_service_details

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        
        # 获取4个最热门的服务
        popular_services = []
        service_views = ServiceView.query.order_by(ServiceView.view_count.desc()).limit(8).all()
        service_details = get_service_details()
        
        # 对于每个热门服务类别，添加服务详情
        for view in service_views:
            if view.service_id in service_details:
                service = service_details[view.service_id]
                service['category'] = view.category
                popular_services.append(service)
                if len(popular_services) >= 4:
                    break
        
        # 如果没有足够的热门服务，添加默认服务
        if len(popular_services) < 4:
            default_services = ['moving', 'pickup', 'housing', 'legal']
            for service_id in default_services:
                if service_id in service_details and not any(s['id'] == service_id for s in popular_services):
                    service = service_details[service_id]
                    # 找到该服务所属的类别
                    for category in SERVICE_CATEGORIES:
                        if any(subcategory[0] == service_id for subcategory in category['subcategories']):
                            service['category'] = category['id']
                            break
                    popular_services.append(service)
                    if len(popular_services) >= 4:
                        break
        
        # 获取热门任务
        featured_tasks = Task.query.order_by(Task.view_count.desc()).limit(3).all()
        
        # 如果没有足够的热门任务，获取最新任务
        if len(featured_tasks) < 3:
            additional_tasks = Task.query.filter(~Task.id.in_([t.id for t in featured_tasks])).order_by(Task.created_at.desc()).limit(3 - len(featured_tasks)).all()
            featured_tasks.extend(additional_tasks)
        
        return render_template('index.html', 
                             popular_services=popular_services, 
                             featured_tasks=featured_tasks,
                             current_user=current_user,
                             search_query=search_query)
                             
    except Exception as e:
        current_app.logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html', 
                             popular_services=[],
                             featured_tasks=[],
                             current_user=current_user,
                             error_message="加载任务时发生错误")

@main_bp.route('/set_language/<language>')
def set_language(language):
    current_app.logger.debug(f"[LANG] Setting language to: {language}")
    current_app.logger.debug(f"[LANG] Current session before: {dict(session)}")
    current_app.logger.debug(f"[LANG] Supported locales: {current_app.config['BABEL_SUPPORTED_LOCALES']}")
    
    if language in current_app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = language
        session.modified = True
        current_app.logger.debug(f"[LANG] Session updated: {dict(session)}")
    else:
        current_app.logger.warning(f"[LANG] Invalid language requested: {language}")
    
    referrer = request.referrer
    current_app.logger.debug(f"[LANG] Referrer URL: {referrer}")
    
    return redirect(referrer or url_for('main.index'))

@main_bp.route('/contact')
def contact():
    return render_template('contact.html')

@main_bp.route('/professionals')
def professionals():
    """专业人士页面，展示可提供的服务和热门/高报酬任务"""
    # 获取所有服务类别
    service_categories = SERVICE_CATEGORIES
    
    # 获取热门任务（按浏览量排序）
    popular_tasks = Task.query.order_by(Task.view_count.desc()).limit(4).all()
    
    # 获取高报酬任务（按预算排序）
    high_paying_tasks = Task.query.order_by(Task.budget.desc()).limit(4).all()
    
    return render_template(
        'professionals.html',
        service_categories=service_categories,
        popular_tasks=popular_tasks,
        high_paying_tasks=high_paying_tasks
    )

@main_bp.route('/our_story')
def our_story():
    return render_template('our_story.html')

@main_bp.route('/user_guide')
def user_guide():
    return render_template('user_guide.html')

@main_bp.route('/service_standards')
def service_standards():
    return render_template('service_standards.html')

@main_bp.route('/user_reviews')
def user_reviews():
    return render_template('user_reviews.html')

@main_bp.route('/blog')
def blog():
    return render_template('blog.html')

@main_bp.route('/pricing_guide')
def pricing_guide():
    return render_template('pricing_guide.html')

@main_bp.route('/faq')
def faq():
    return render_template('faq.html')

@main_bp.route('/why_choose_us')
def why_choose_us():
    return render_template('why_choose_us.html')

@main_bp.route('/become_provider')
def become_provider():
    return render_template('become_provider.html')

@main_bp.route('/search/suggestions')
def search_suggestions():
    query = request.args.get('q', '').strip().lower()
    print(f"接收到搜索建议请求，查询词: {query}")
    
    if not query or len(query) < 1:
        print("查询词为空或太短，返回空列表")
        return jsonify([])
    
    # 从服务类别中搜索匹配的服务
    results = []
    
    for category in SERVICE_CATEGORIES:
        category_name = category['name']
        category_id = category['id']
        
        # 检查主类别是否匹配
        if query in category_name.lower():
            # 添加整个类别作为建议
            result = {
                'id': category_id,
                'title': category_name,
                'type': 'category'
            }
            print(f"找到匹配的类别: {result}")
            results.append(result)
        
        # 检查子类别是否匹配
        for subcategory in category['subcategories']:
            service_id, service_name = subcategory
            
            # 如果查询是服务名称的前缀或包含在服务名称中
            if service_name.lower().startswith(query) or query in service_name.lower():
                result = {
                    'id': service_id,
                    'title': service_name,
                    'type': 'service'
                }
                print(f"找到匹配的服务: {result}")
                results.append(result)
    
    # 按相关性排序：优先显示以查询开头的结果
    results.sort(key=lambda x: (0 if x['title'].lower().startswith(query) else 1, x['title']))
    
    # 限制结果数量
    final_results = results[:8]
    print(f"返回 {len(final_results)} 个搜索建议")
    return jsonify(final_results) 