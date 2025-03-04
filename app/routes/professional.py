from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import User, Task, Message, Review
from sqlalchemy import and_, or_, func
from datetime import datetime, timedelta

professional_bp = Blueprint('professional', __name__, url_prefix='/professional')

@professional_bp.before_request
def check_professional():
    """确保只有专业人士才能访问专业人士页面"""
    if not current_user.is_authenticated:
        flash('请先登录专业人士账户', 'warning')
        return redirect(url_for('auth.professional_login'))
    
    if not current_user.is_professional:
        flash('您需要专业人士账户才能访问此页面', 'warning')
        return redirect(url_for('main.index'))

@professional_bp.route('/dashboard')
@login_required
def dashboard():
    """专业人士控制面板，显示概览信息"""
    # 获取进行中的任务数量
    active_tasks = Task.query.filter(
        Task.executor_id == current_user.id,
        Task.status.in_([1, 2])  # 1: 等待执行, 2: 进行中
    ).count()
    
    # 获取已完成的任务数量
    completed_tasks = Task.query.filter(
        Task.executor_id == current_user.id,
        Task.status == 3  # 3: 已完成
    ).count()
    
    # 获取最近30天内的收入
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_income = db.session.query(func.sum(Task.budget)).filter(
        Task.executor_id == current_user.id,
        Task.status == 3,  # 已完成
        Task.updated_at >= thirty_days_ago
    ).scalar() or 0
    
    # 获取未读消息数量
    unread_messages = Message.query.filter(
        Message.recipient_id == current_user.id,
        Message.read == False
    ).count()
    
    # 获取评价总数和平均分
    reviews = Review.query.filter_by(reviewee_id=current_user.id).all()
    avg_rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
    
    # 获取最近的任务
    recent_tasks = Task.query.filter(
        Task.executor_id == current_user.id
    ).order_by(Task.updated_at.desc()).limit(5).all()
    
    # 推荐任务：匹配专业人士技能的开放任务
    skills_list = current_user.skills.split(',') if current_user.skills else []
    skill_filters = []
    for skill in skills_list:
        skill = skill.strip()
        if skill:
            skill_filters.append(or_(
                Task.title.ilike(f'%{skill}%'),
                Task.description.ilike(f'%{skill}%'),
                Task.service_category.ilike(f'%{skill}%')
            ))
    
    recommended_tasks = []
    if skill_filters:
        recommended_tasks = Task.query.filter(
            Task.status == 0,  # 等待接单
            Task.executor_id == None,
            or_(*skill_filters)
        ).order_by(Task.created_at.desc()).limit(5).all()
    
    return render_template('professional/dashboard.html',
                          active_tasks=active_tasks,
                          completed_tasks=completed_tasks,
                          recent_income=recent_income,
                          unread_messages=unread_messages,
                          reviews_count=len(reviews),
                          avg_rating=avg_rating,
                          recent_tasks=recent_tasks,
                          recommended_tasks=recommended_tasks)

@professional_bp.route('/tasks')
@login_required
def tasks():
    """显示专业人士的所有任务"""
    status_filter = request.args.get('status', 'all')
    page = request.args.get('page', 1, type=int)
    
    # 构建查询
    query = Task.query.filter(Task.executor_id == current_user.id)
    
    # 应用状态过滤
    if status_filter == 'active':
        query = query.filter(Task.status.in_([1, 2]))  # 等待执行、进行中
    elif status_filter == 'completed':
        query = query.filter(Task.status == 3)  # 已完成
    elif status_filter == 'cancelled':
        query = query.filter(Task.status == 4)  # 已取消
    
    # 分页
    tasks = query.order_by(Task.updated_at.desc()).paginate(
        page=page, per_page=current_app.config['TASKS_PER_PAGE'], error_out=False
    )
    
    return render_template('professional/tasks.html',
                          tasks=tasks,
                          status_filter=status_filter)

@professional_bp.route('/profile')
@login_required
def professional_profile():
    """显示和编辑专业人士档案"""
    # 获取专业人士的评价
    reviews = Review.query.filter_by(reviewee_id=current_user.id).all()
    
    return render_template('professional/profile.html',
                          user=current_user,
                          reviews=reviews)

@professional_bp.route('/messages')
@login_required
def messages():
    """显示专业人士的消息"""
    page = request.args.get('page', 1, type=int)
    
    # 获取所有对话
    conversations = db.session.query(
        Message.sender_id,
        func.max(Message.timestamp).label('last_timestamp')
    ).filter(
        Message.recipient_id == current_user.id
    ).group_by(Message.sender_id).order_by(func.max(Message.timestamp).desc()).all()
    
    conversation_users = []
    for sender_id, _ in conversations:
        user = User.query.get(sender_id)
        if user:
            # 获取最新消息和未读消息数
            latest_message = Message.query.filter(
                Message.sender_id == sender_id,
                Message.recipient_id == current_user.id
            ).order_by(Message.timestamp.desc()).first()
            
            unread_count = Message.query.filter(
                Message.sender_id == sender_id,
                Message.recipient_id == current_user.id,
                Message.read == False
            ).count()
            
            conversation_users.append({
                'user': user,
                'latest_message': latest_message,
                'unread_count': unread_count
            })
    
    return render_template('professional/messages.html',
                          conversations=conversation_users)

@professional_bp.route('/market')
@login_required
def market():
    """任务市场，显示可接的任务"""
    category_filter = request.args.get('category', 'all')
    sort_by = request.args.get('sort', 'latest')
    page = request.args.get('page', 1, type=int)
    
    # 构建基本查询：未分配执行者且状态为等待接单的任务
    query = Task.query.filter(
        Task.status == 0,  # 等待接单
        Task.executor_id == None
    )
    
    # 应用类别过滤
    if category_filter != 'all':
        query = query.filter(or_(
            Task.service_main_category == category_filter,
            Task.service_sub_category == category_filter
        ))
    
    # 应用排序
    if sort_by == 'budget_high':
        query = query.order_by(Task.budget.desc())
    elif sort_by == 'budget_low':
        query = query.order_by(Task.budget.asc())
    else:  # latest
        query = query.order_by(Task.created_at.desc())
    
    # 分页
    tasks = query.paginate(
        page=page, per_page=current_app.config['TASKS_PER_PAGE'], error_out=False
    )
    
    return render_template('professional/market.html',
                          tasks=tasks,
                          category_filter=category_filter,
                          sort_by=sort_by) 