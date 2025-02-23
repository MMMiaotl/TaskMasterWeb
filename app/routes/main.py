from flask import Blueprint, render_template, request, current_app, session, redirect, url_for, jsonify
from app.models import Task
from sqlalchemy import or_
from flask_login import current_user
import time

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
@main_bp.route('/index')
def index():
    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        
        # 基本查询
        base_query = Task.query.order_by(Task.created_at.desc())
        
        # 如果有搜索词，添加搜索条件
        if search_query:
            base_query = base_query.filter(
                or_(
                    Task.title.ilike(f'%{search_query}%'),
                    Task.description.ilike(f'%{search_query}%')
                )
            )
        
        # 执行查询
        tasks = base_query.limit(10).all()
        
        return render_template('index.html', 
                             tasks=tasks,
                             current_user=current_user,
                             search_query=search_query)
                             
    except Exception as e:
        current_app.logger.error(f"Error in index route: {str(e)}")
        return render_template('index.html', 
                             tasks=[],
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