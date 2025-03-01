from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import current_user, login_required
from app import db
from app.models import Task, Message, User, Review
from app.forms import TaskForm, ReviewForm
from sqlalchemy import or_
from datetime import datetime
from app.utils.constants import SERVICE_CATEGORIES, SERVICE_CHOICES
from flask import current_app

task_bp = Blueprint('task', __name__, url_prefix='/task')

@task_bp.route('/tasks')
def tasks():
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
        tasks = base_query.all()
        return render_template('tasks.html', tasks=tasks)
    except Exception as e:
        flash('加载任务列表时发生错误')
        return render_template('tasks.html', tasks=[])

@task_bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    
    # 处理GET请求中的category参数
    if request.method == 'GET' and request.args.get('category'):
        category_name = request.args.get('category')
        # 查找匹配的服务类别
        for value, label in SERVICE_CHOICES:
            if category_name.lower() in label.lower():
                form.service_category.data = value
                break
    
    if form.validate_on_submit():
        try:
            # 创建基本任务对象
            task = Task(
                title=form.title.data if form.title.data else "未命名任务",
                description=form.description.data if form.description.data else "",
                service_category=form.service_category.data,
                location=form.location.data,
                deadline=form.deadline.data,
                budget=form.budget.data,
                user_id=current_user.id
            )
            
            # 处理补充信息
            if form.additional_info.data:
                # 这里可以将补充信息添加到描述中或存储在单独的字段中
                if task.description:
                    task.description += "\n\n补充信息：\n" + form.additional_info.data
                else:
                    task.description = "补充信息：\n" + form.additional_info.data
            
            # 处理图片上传
            if form.task_images.data:
                # 这里需要实现图片上传和存储的逻辑
                # 例如：保存图片到服务器，并将路径存储到数据库
                # 这部分代码需要根据你的文件存储方式来实现
                pass
            
            # 根据服务类别处理特定字段
            if task.service_category:
                # 解析服务类别
                try:
                    main_cat, sub_cat = task.service_category.split('.')
                    
                    # 搬家服务特定字段
                    if sub_cat == 'moving':
                        task.moving_item_size = form.moving_item_size.data
                        task.moving_item_quantity = form.moving_item_quantity.data
                        task.moving_has_elevator = form.moving_has_elevator.data
                        task.moving_floor_number = form.moving_floor_number.data
                    
                    # 接送机特定字段
                    elif sub_cat == 'pickup':
                        task.pickup_flight_number = form.pickup_flight_number.data
                        task.pickup_passengers = form.pickup_passengers.data
                        task.pickup_luggage_count = form.pickup_luggage_count.data
                        task.pickup_is_arrival = form.pickup_is_arrival.data == '1' if form.pickup_is_arrival.data else None
                    
                    # 装修维修特定字段
                    elif sub_cat == 'repair':
                        task.repair_area = form.repair_area.data
                        task.repair_type = form.repair_type.data
                        task.repair_materials_included = form.repair_materials_included.data
                        # 添加新的装修翻新字段
                        task.repair_address = form.repair_address.data
                        task.repair_work_painting = form.repair_work_painting.data
                        task.repair_work_plastering = form.repair_work_plastering.data
                        task.repair_work_flooring = form.repair_work_flooring.data
                        task.repair_work_plumbing = form.repair_work_plumbing.data
                        task.repair_work_bathroom = form.repair_work_bathroom.data
                        task.repair_work_toilet = form.repair_work_toilet.data
                        task.repair_work_kitchen = form.repair_work_kitchen.data
                        task.repair_work_garden = form.repair_work_garden.data
                        task.repair_work_extension = form.repair_work_extension.data
                        task.repair_work_other = form.repair_work_other.data
                    
                    # 法律咨询特定字段
                    elif sub_cat == 'legal':
                        task.legal_case_type = form.legal_case_type.data
                        task.legal_urgency = form.legal_urgency.data
                        task.legal_documents_ready = form.legal_documents_ready.data
                    
                    # 留学咨询特定字段
                    elif sub_cat == 'education':
                        task.education_target_country = form.education_target_country.data
                        task.education_study_level = form.education_study_level.data
                        task.education_field = form.education_field.data
                        
                except ValueError:
                    # 如果格式不正确，记录日志
                    current_app.logger.warning(f"Invalid service category format: {task.service_category}")
            
            db.session.add(task)
            db.session.commit()
            flash('任务发布成功！', 'success')
            return redirect(url_for('task.tasks'))
        except Exception as e:
            db.session.rollback()
            flash('发布任务时出错：' + str(e), 'danger')
            return redirect(url_for('task.create_task'))
    
    return render_template('create_task.html', 
                         title='发布任务', 
                         form=form,
                         categories=SERVICE_CATEGORIES,
                         preselect_category=request.args.get('category', ''))

@task_bp.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 增加浏览计数，确保 view_count 不是 None
    if task.view_count is None:
        task.view_count = 1
    else:
        task.view_count += 1
    db.session.commit()
    
    # 获取感兴趣的用户（发送过消息的用户）
    interested_users = set()
    for message in task.messages:
        if message.sender_id != task.author.id:
            interested_users.add(message.sender)
    
    # 获取平台推荐用户（这里可以根据你的推荐算法实现）
    recommended_users = User.query.filter(
        User.id != task.author.id
    ).order_by(
        db.func.random()
    ).limit(5).all()
    
    return render_template('task_detail.html', 
                         task=task,
                         interested_users=interested_users,
                         recommended_users=recommended_users)

@task_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('你没有权限编辑这个任务')
        return redirect(url_for('task.tasks'))
    
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.service_category = form.service_category.data
        task.location = form.location.data
        task.deadline = form.deadline.data
        task.budget = form.budget.data
        db.session.commit()
        flash('任务已更新')
        return redirect(url_for('task.task_detail', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.description.data = task.description
        form.service_category.data = task.service_category
        form.location.data = task.location
        form.deadline.data = task.deadline
        form.budget.data = task.budget

    return render_template('edit_task.html', title='编辑任务', form=form, task=task)

@task_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You cannot delete this task.')
        return redirect(url_for('task.tasks'))
    
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted.')
    return redirect(url_for('task.tasks'))

@task_bp.route('/task/<int:task_id>/conversation', methods=['GET', 'POST'])
@login_required
def task_conversation(task_id):
    task = Task.query.get_or_404(task_id)
    user_tasks = Task.query.filter_by(user_id=current_user.id).order_by(Task.created_at.desc()).all()  # 查询当前用户的所有任务
    
    if request.method == 'POST':
        content = request.form.get('content')
        if content:
            recipient_id = task.user_id
            message = Message(
                content=content,
                sender_id=current_user.id,
                recipient_id=recipient_id,
                task_id=task_id,
                created_at=datetime.utcnow()
            )
            db.session.add(message)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'message': {
                    'content': message.content,
                    'sender': message.sender.username,
                    'created_at': message.created_at.strftime('%Y-%m-%d %H:%M')
                }
            })
        return jsonify({'success': False, 'error': '内容不能为空'})
    
    messages = Message.query.filter_by(task_id=task_id).order_by(Message.created_at.asc()).all()
    return render_template('task_conversation.html', task=task, messages=messages, user_tasks=user_tasks)

@task_bp.route('/task/<int:task_id>/invite/<int:user_id>', methods=['POST'])
@login_required
def send_invitation(task_id, user_id):
    task = Task.query.get_or_404(task_id)
    user = User.query.get_or_404(user_id)
    
    # 检查当前用户是否有权限发送邀请
    if task.author != current_user:
        flash('你没有权限发送邀请', 'error')
        return redirect(url_for('task.task_detail', task_id=task_id))
    
    # 检查任务状态
    if task.status != 0:  # 0 表示等待接单
        flash('该任务已经有人接单', 'warning')
        return redirect(url_for('task.task_detail', task_id=task_id))
    
    try:
        # 创建邀请消息
        message = Message(
            content=f"{current_user.username} 邀请你参与任务：{task.title}。是否接受？",
            sender_id=current_user.id,
            recipient_id=user_id,
            task_id=task_id,
            is_invitation=True,
            created_at=datetime.utcnow()  # 确保时间戳被记录
        )
        db.session.add(message)
        db.session.commit()
        
        flash('邀请已发送', 'success')
    except Exception as e:
        db.session.rollback()
        flash('发送邀请时出错：' + str(e), 'error')
    
    return redirect(url_for('task.task_detail', task_id=task_id))

@task_bp.route('/task/invitation/<int:message_id>/accept', methods=['POST'])
@login_required
def accept_invitation(message_id):
    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id:
        flash('你没有权限接受这个邀请', 'error')
        return redirect(url_for('task.tasks'))
    
    task = Task.query.get_or_404(message.task_id)
    task.status = 1  # 假设1表示已接单
    db.session.commit()
    flash('你已接受邀请', 'success')
    return redirect(url_for('task.task_detail', task_id=task.id))

@task_bp.route('/task/invitation/<int:message_id>/reject', methods=['POST'])
@login_required
def reject_invitation(message_id):
    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id:
        flash('你没有权限拒绝这个邀请', 'error')
        return redirect(url_for('task.tasks'))
    
    flash('你已拒绝邀请', 'info')
    return redirect(url_for('task.tasks'))

@task_bp.route('/task/<int:task_id>/respond_invitation', methods=['POST'])
@login_required
def respond_invitation(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 检查当前用户是否被邀请
    if not current_user.invited_tasks.filter_by(id=task_id).first():
        flash('你没有权限响应此邀请', 'error')
        return redirect(url_for('user.user_profile', username=current_user.username))
    
    response = request.form.get('response')
    if response == 'accept':
        # 处理接受邀请的逻辑
        task.status = 1  # 假设1表示已接单
        task.executor_id = current_user.id
        flash('你已成功接受任务邀请', 'success')
    elif response == 'reject':
        # 处理拒绝邀请的逻辑
        flash('你已拒绝任务邀请', 'info')
    else:
        flash('无效的响应', 'error')
    
    db.session.commit()
    return redirect(url_for('user.user_profile', username=current_user.username))

@task_bp.route('/task/<int:task_id>/update_status', methods=['POST'])
@login_required
def update_task_status(task_id):
    task = Task.query.get_or_404(task_id)
    new_status = int(request.form.get('status'))

    # 检查权限
    if (new_status == 2 and current_user.id != task.executor_id) or \
       (new_status == 3 and current_user.id != task.user_id):
        flash('你没有权限执行此操作', 'error')
        return redirect(url_for('task.task_detail', task_id=task_id))

    # 更新状态
    task.status = new_status
    db.session.commit()

    flash('任务状态已更新', 'success')
    return redirect(url_for('task.task_detail', task_id=task_id))

@task_bp.route('/task/<int:task_id>/review_executor', methods=['GET', 'POST'])
@login_required
def review_executor(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 验证是否已评价
    existing_review = Review.query.filter_by(
        task_id=task_id,
        reviewer_id=current_user.id
    ).first()
    
    if existing_review:
        flash('您已经评价过该任务', 'warning')
        return redirect(url_for('task.task_detail', task_id=task_id))

    # 权限验证
    if current_user.id not in [task.user_id, task.executor_id]:
        flash('您无权进行此操作', 'error')
        return redirect(url_for('task.task_detail', task_id=task.id))

    # 自动确定评价角色
    is_executor = (current_user.id == task.executor_id)
    reviewee_id = task.user_id if is_executor else task.executor_id
    role = 'poster' if is_executor else 'executor'  # 关键修改点

    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        content = request.form.get('comment')

        review = Review(
            rating=rating,
            content=content,
            reviewer_id=current_user.id,
            reviewee_id=reviewee_id,
            task_id=task_id,
            role=role  # 使用动态设置的角色
        )
        db.session.add(review)
        db.session.commit()
        flash('评价已提交', 'success')
        return redirect(url_for('task.task_detail', task_id=task_id))

    return render_template('review_executor.html', task=task)

@task_bp.route('/search/suggestions')
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