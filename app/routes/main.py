from flask import Blueprint, render_template, request, current_app, session, redirect, url_for
from app.models import Task
from sqlalchemy import or_
from flask_login import current_user

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
    if language in current_app.config.get('BABEL_SUPPORTED_LOCALES', ['en', 'zh']):
        session['lang'] = language
    return redirect(request.referrer or url_for('main.index'))

@main_bp.route('/contact')
def contact():
    return render_template('contact.html') 