from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, abort
from flask_login import current_user, login_required
from app import db
from app.models import User, Task, Message, Review
from datetime import datetime, timedelta
from sqlalchemy import func
import json

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# 管理员权限检查装饰器
def admin_required(f):
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            abort(403)  # 无权限访问
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return login_required(decorated_function)

# 管理员仪表盘
@admin_bp.route('/')
@admin_required
def dashboard():
    # 获取基本统计数据
    total_users = User.query.count()
    total_tasks = Task.query.count()
    total_messages = Message.query.count()
    
    # 获取最近注册的用户
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # 获取最近创建的任务
    recent_tasks = Task.query.order_by(Task.created_at.desc()).limit(5).all()
    
    # 获取时间范围数据
    now = datetime.now()
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    three_months_ago = now - timedelta(days=90)
    year_ago = now - timedelta(days=365)
    
    # 用户统计
    day_users = User.query.filter(User.created_at >= day_ago).count()
    week_users = User.query.filter(User.created_at >= week_ago).count()
    month_users = User.query.filter(User.created_at >= month_ago).count()
    three_months_users = User.query.filter(User.created_at >= three_months_ago).count()
    year_users = User.query.filter(User.created_at >= year_ago).count()
    
    # 任务统计
    day_tasks = Task.query.filter(Task.created_at >= day_ago).count()
    week_tasks = Task.query.filter(Task.created_at >= week_ago).count()
    month_tasks = Task.query.filter(Task.created_at >= month_ago).count()
    three_months_tasks = Task.query.filter(Task.created_at >= three_months_ago).count()
    year_tasks = Task.query.filter(Task.created_at >= year_ago).count()
    
    # 按状态统计任务
    tasks_by_status = db.session.query(
        Task.status, func.count(Task.id)
    ).group_by(Task.status).all()
    
    # 专业人士统计
    total_pros = User.query.filter_by(is_professional=True).count()
    
    return render_template('admin/dashboard.html',
                          total_users=total_users,
                          total_tasks=total_tasks,
                          total_messages=total_messages,
                          total_pros=total_pros,
                          recent_users=recent_users,
                          recent_tasks=recent_tasks,
                          day_users=day_users,
                          week_users=week_users,
                          month_users=month_users,
                          three_months_users=three_months_users,
                          year_users=year_users,
                          day_tasks=day_tasks,
                          week_tasks=week_tasks,
                          month_tasks=month_tasks,
                          three_months_tasks=three_months_tasks,
                          year_tasks=year_tasks,
                          tasks_by_status=tasks_by_status)

# 用户管理
@admin_bp.route('/users')
@admin_required
def users():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    role_filter = request.args.get('role', '')
    
    query = User.query
    
    # 搜索过滤
    if search:
        query = query.filter(
            (User.username.contains(search)) |
            (User.email.contains(search))
        )
    
    # 角色过滤
    if role_filter == 'admin':
        query = query.filter(User.role == 'admin')
    elif role_filter == 'professional':
        query = query.filter(User.is_professional == True)
    elif role_filter == 'regular':
        query = query.filter(User.is_professional == False, User.role == 'user')
    
    # 分页
    users = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/users.html', users=users, 
                          search=search, role_filter=role_filter)

# 任务管理
@admin_bp.route('/tasks')
@admin_required
def tasks():
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '')
    status_filter = request.args.get('status', '')
    
    query = Task.query
    
    # 搜索过滤
    if search:
        query = query.filter(Task.title.contains(search))
    
    # 状态过滤
    if status_filter:
        query = query.filter(Task.status == status_filter)
    
    # 分页
    tasks = query.order_by(Task.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('admin/tasks.html', tasks=tasks,
                          search=search, status_filter=status_filter)

# 获取图表数据API
@admin_bp.route('/api/chart/users')
@admin_required
def chart_users():
    # 获取过去30天的用户注册数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 按日期分组查询
    user_stats = db.session.query(
        func.date(User.created_at).label('date'),
        func.count(User.id).label('count')
    ).filter(
        User.created_at.between(start_date, end_date)
    ).group_by(
        func.date(User.created_at)
    ).all()
    
    # 格式化数据
    dates = []
    counts = []
    
    for stat in user_stats:
        if hasattr(stat.date, 'strftime') and callable(stat.date.strftime):
            dates.append(stat.date.strftime('%Y-%m-%d'))
        else:
            dates.append(str(stat.date))
        counts.append(stat.count)
    
    return jsonify({
        'labels': dates,
        'data': counts
    })

# 获取任务图表数据API
@admin_bp.route('/api/chart/tasks')
@admin_required
def chart_tasks():
    # 获取过去30天的任务创建数据
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    # 按日期分组查询
    task_stats = db.session.query(
        func.date(Task.created_at).label('date'),
        func.count(Task.id).label('count')
    ).filter(
        Task.created_at.between(start_date, end_date)
    ).group_by(
        func.date(Task.created_at)
    ).all()
    
    # 格式化数据
    dates = []
    counts = []
    
    for stat in task_stats:
        if hasattr(stat.date, 'strftime') and callable(stat.date.strftime):
            dates.append(stat.date.strftime('%Y-%m-%d'))
        else:
            dates.append(str(stat.date))
        counts.append(stat.count)
    
    return jsonify({
        'labels': dates,
        'data': counts
    })

# 系统设置
@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'POST':
        # 处理设置更新
        # 这里可以添加网站设置的保存逻辑
        flash('设置已更新', 'success')
        return redirect(url_for('admin.settings'))
    
    return render_template('admin/settings.html')

# 用户API - 更新用户信息
@admin_bp.route('/api/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    data = request.json
    
    try:
        # 更新邮箱
        if 'email' in data and data['email'] != user.email:
            # 检查邮箱是否已存在
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({
                    'success': False,
                    'message': '该邮箱已被使用'
                }), 400
            user.email = data['email']
        
        # 更新角色
        if 'role' in data:
            if data['role'] == 'admin':
                user.role = 'admin'
                user.is_professional = False
            elif data['role'] == 'professional':
                user.role = 'user'
                user.is_professional = True
            else:
                user.role = 'user'
                user.is_professional = False
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '用户信息已更新'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

# 用户API - 切换用户状态
@admin_bp.route('/api/users/<int:user_id>/toggle-status', methods=['POST'])
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    # 不允许管理员禁用自己
    if user.id == current_user.id and user.is_admin():
        return jsonify({
            'success': False,
            'message': '不能禁用当前登录的管理员账户'
        }), 400
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = '启用' if user.is_active else '禁用'
        
        return jsonify({
            'success': True,
            'message': f'用户已{status}',
            'is_active': user.is_active
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500

# 任务API - 更新任务信息
@admin_bp.route('/api/tasks/<int:task_id>', methods=['PUT'])
@admin_required
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    data = request.json
    
    try:
        # 更新标题
        if 'title' in data:
            task.title = data['title']
        
        # 更新状态
        if 'status' in data:
            task.status = data['status']
        
        # 更新预算
        if 'budget' in data:
            task.budget = float(data['budget'])
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务信息已更新'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'更新失败: {str(e)}'
        }), 500

# 任务API - 取消任务
@admin_bp.route('/api/tasks/<int:task_id>/cancel', methods=['POST'])
@admin_required
def cancel_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    try:
        task.status = 'cancelled'
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': '任务已取消'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'message': f'操作失败: {str(e)}'
        }), 500 