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

@main_bp.route('/our_story')
def our_story():
    return render_template('our_story.html')

@main_bp.route('/search/suggestions')
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