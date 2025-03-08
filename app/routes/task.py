from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app, abort
from flask_login import current_user, login_required
from app import db, csrf
from app.models import Task, Message, User, Review, UserCategory
from app.forms import TaskForm, ReviewForm
from sqlalchemy import or_
from datetime import datetime
from app.utils.constants import SERVICE_CATEGORIES, SERVICE_CHOICES

task_bp = Blueprint('task', __name__, url_prefix='/task')

@task_bp.route('/tasks')
def tasks():
    try:
        page = request.args.get('page', 1, type=int)
        search_query = request.args.get('q', '')
        
        # 基本查询
        base_query = Task.query.order_by(Task.created_at.desc())
        
        # 用户权限控制
        access_granted = True
        error_message = ""
        
        if current_user.is_authenticated:
            if current_user.is_admin():
                # 管理员可以查看所有任务
                pass
            elif current_user.is_professional:
                # 专业人士只能看到自己的任务和与其专业类别相关的任务
                user_categories = current_user.get_category_ids()
                category_filters = []
                for category_id in user_categories:
                    if '.' in category_id:
                        main_cat, sub_cat = category_id.split('.')
                        category_filters.append(
                            (Task.service_main_category == main_cat) & 
                            (Task.service_sub_category == sub_cat)
                        )
                
                if category_filters:
                    # 构建 OR 条件：自己的任务 OR 与专业类别相关的任务
                    base_query = base_query.filter(
                        or_(
                            Task.user_id == current_user.id,
                            *category_filters
                        )
                    )
                else:
                    # 如果没有注册专业类别，则只显示自己的任务
                    base_query = base_query.filter(Task.user_id == current_user.id)
            else:
                # 普通用户只能看到自己的任务
                base_query = base_query.filter(Task.user_id == current_user.id)
        else:
            # 未登录用户显示权限错误提示
            access_granted = False
            error_message = '请先登录后查看任务列表'
            flash(error_message, 'info')
        
        # 如果有搜索词，添加搜索条件
        if search_query:
            base_query = base_query.filter(
                or_(
                    Task.title.ilike(f'%{search_query}%'),
                    Task.description.ilike(f'%{search_query}%')
                )
            )
        
        # 执行查询
        tasks = base_query.all() if access_granted else []
        
        return render_template('tasks.html', 
                              tasks=tasks, 
                              search_query=search_query,
                              access_denied=not access_granted,
                              error_message=error_message)
    except Exception as e:
        current_app.logger.error(f"加载任务列表时出错: {str(e)}")
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
            flash(f'任务发布成功！您现在可以查看任务详情或邀请服务提供者。', 'success')
            return redirect(url_for('task.task_detail', task_id=task.id))
        except Exception as e:
            db.session.rollback()
            flash('发布任务时出错：' + str(e), 'danger')
            return redirect(url_for('task.create_task'))
    
    return render_template('create_task.html', 
                         title='发布任务', 
                         form=form,
                         categories=SERVICE_CATEGORIES,
                         preselect_category=request.args.get('category', ''))

@task_bp.route('/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 权限检查
    access_granted = True
    error_message = ""
    
    if current_user.is_authenticated:
        if current_user.is_admin():
            # 管理员可以查看所有任务
            pass
        elif current_user.is_professional:
            # 专业人士只能查看自己的任务和与其专业类别相关的任务
            if task.user_id != current_user.id:
                category_id = f"{task.service_main_category}.{task.service_sub_category}"
                if not current_user.has_category(category_id):
                    access_granted = False
                    error_message = '您没有权限查看此任务，因为它不属于您注册的服务类别'
                    flash(error_message, 'warning')
        else:
            # 普通用户只能查看自己的任务
            if task.user_id != current_user.id:
                access_granted = False
                error_message = '普通用户只能查看自己发布的任务'
                flash(error_message, 'warning')
    else:
        # 未登录用户无权查看任务详情
        access_granted = False
        error_message = '请先登录后再查看任务详情'
        flash(error_message, 'info')
    
    # 增加浏览量
    task.view_count += 1
    db.session.commit()
    
    # 获取推荐的专业人士
    recommended_users = []
    if current_user.is_authenticated and task.user_id == current_user.id and task.status == 0:
        # 仅对任务发布者且任务状态为等待接单时显示推荐
        recommended_users = get_recommended_users_for_task(task)
    
    return render_template('task_detail.html', 
                          task=task, 
                          recommended_users=recommended_users,
                          access_denied=not access_granted,
                          error_message=error_message)

@task_bp.route('/<int:task_id>/edit', methods=['GET', 'POST'])
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

@task_bp.route('/<int:task_id>/delete', methods=['POST'])
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

@task_bp.route('/<int:task_id>/cancel', methods=['POST'])
@login_required
def cancel_task(task_id):
    task = Task.query.get_or_404(task_id)
    
    # 检查是否是任务发布者
    if task.user_id != current_user.id:
        flash('您没有权限取消这个任务', 'danger')
        return redirect(url_for('task.task_detail', task_id=task.id))
    
    # 检查任务状态是否允许取消
    if task.status > 1:  # 如果任务已经开始执行或已完成，不允许取消
        flash('任务已经开始执行或已完成，无法取消', 'warning')
        return redirect(url_for('task.task_detail', task_id=task.id))
    
    # 更新任务状态为已取消
    task.status = 4  # 已取消状态
    db.session.commit()
    
    flash('任务已成功取消', 'success')
    return redirect(url_for('task.tasks'))

@task_bp.route('/<int:task_id>/conversation', methods=['GET', 'POST'])
@login_required
def task_conversation(task_id):
    """处理任务对话页面和消息发送"""
    try:
        # 获取任务信息
        task = Task.query.get_or_404(task_id)
        
        # 如果是GET请求，显示对话页面
        if request.method == 'GET':
            # 获取对话对象
            pro_id = request.args.get('pro_id', type=int)
            if pro_id:
                pro = User.query.get_or_404(pro_id)
                
                # 检查权限（任务创建者或被选中的专业人士才能查看）
                is_creator = task.user_id == current_user.id
                is_executor = task.executor_id == current_user.id
                if not (is_creator or is_executor or pro_id == current_user.id):
                    flash('您无权访问此对话', 'danger')
                    return redirect(url_for('task.task_detail', task_id=task_id))
                
                # 查询与任务和专业人士相关的所有消息
                messages = Message.query.filter(
                    (Message.task_id == task_id) &
                    (
                        ((Message.sender_id == current_user.id) & (Message.recipient_id == pro_id)) |
                        ((Message.recipient_id == current_user.id) & (Message.sender_id == pro_id))
                    )
                ).order_by(Message.created_at.asc()).all()
                
                # 标记消息为已读
                for msg in messages:
                    if msg.recipient_id == current_user.id and not msg.is_read:
                        msg.is_read = True
                db.session.commit()
                
                return render_template('task_conversation.html', 
                                       task=task,
                                       pro=pro,
                                       messages=messages)
            else:
                flash('未指定对话对象', 'warning')
                return redirect(url_for('task.task_detail', task_id=task_id))
        
        # 如果是POST请求，处理消息发送
        elif request.method == 'POST':
            # 获取消息内容和接收者ID
            content = request.form.get('content') or request.json.get('content')
            recipient_id = request.form.get('recipient_id') or request.json.get('recipient_id')
            
            # 检查参数
            if not content or not recipient_id:
                if request.is_json:
                    return jsonify({"success": False, "error": "消息内容和接收者ID不能为空"}), 400
                else:
                    flash('消息内容和接收者ID不能为空', 'danger')
                    return redirect(request.referrer or url_for('task.task_detail', task_id=task_id))
            
            try:
                recipient_id = int(recipient_id)
            except ValueError:
                if request.is_json:
                    return jsonify({"success": False, "error": "接收者ID必须是整数"}), 400
                else:
                    flash('接收者ID必须是整数', 'danger')
                    return redirect(request.referrer or url_for('task.task_detail', task_id=task_id))
            
            # 获取接收者
            recipient = User.query.get(recipient_id)
            if not recipient:
                if request.is_json:
                    return jsonify({"success": False, "error": "接收者不存在"}), 404
                else:
                    flash('接收者不存在', 'danger')
                    return redirect(request.referrer or url_for('task.task_detail', task_id=task_id))
            
            # 创建消息
            message = Message(
                content=content,
                sender_id=current_user.id,
                recipient_id=recipient_id,
                task_id=task_id,
                created_at=datetime.utcnow()
            )
            db.session.add(message)
            db.session.commit()
            
            # 根据请求类型返回响应
            if request.is_json:
                return jsonify({
                    "success": True,
                    "message": {
                        "id": message.id,
                        "content": message.content,
                        "sender_id": message.sender_id,
                        "recipient_id": message.recipient_id,
                        "created_at": message.created_at.isoformat(),
                        "is_read": message.is_read
                    }
                })
            else:
                flash('消息已发送', 'success')
                return redirect(url_for('task.task_conversation', task_id=task_id, pro_id=recipient_id))
            
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in task_conversation: {str(e)}")
        if request.is_json:
            return jsonify({"success": False, "error": str(e)}), 500
        else:
            flash('处理对话时发生错误', 'danger')
            return redirect(url_for('task.task_detail', task_id=task_id))

@task_bp.route('/<int:task_id>/invite/<int:user_id>', methods=['POST'])
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

@task_bp.route('/invitation/<int:message_id>/accept', methods=['POST'])
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

@task_bp.route('/invitation/<int:message_id>/reject', methods=['POST'])
@login_required
def reject_invitation(message_id):
    message = Message.query.get_or_404(message_id)
    if message.recipient_id != current_user.id:
        flash('你没有权限拒绝这个邀请', 'error')
        return redirect(url_for('task.tasks'))
    
    flash('你已拒绝邀请', 'info')
    return redirect(url_for('task.tasks'))

@task_bp.route('/<int:task_id>/respond_invitation', methods=['POST'])
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

@task_bp.route('/<int:task_id>/update_status', methods=['POST'])
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

@task_bp.route('/<int:task_id>/review_executor', methods=['GET', 'POST'])
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

@task_bp.route('/<int:task_id>/responses')
@login_required
def task_responses(task_id):
    """显示任务的回应页面，包括对话、感兴趣的专业人士和符合要求的专业人士"""
    try:
        # 添加调试日志
        current_app.logger.info(f"开始加载任务回应页面，任务ID: {task_id}, 用户ID: {current_user.id}")
        
        # 获取任务信息
        task = Task.query.get_or_404(task_id)
        current_app.logger.info(f"成功获取任务信息: {task.title}")
        
        # 检查当前用户是否为任务创建者
        if task.user_id != current_user.id:
            current_app.logger.warning(f"权限错误: 用户 {current_user.id} 尝试访问任务 {task_id} 的回应页面，但不是任务创建者")
            flash('您无权访问此页面', 'danger')
            return redirect(url_for('task.tasks'))
        
        # 查询与任务相关的所有对话
        current_app.logger.info(f"开始查询任务相关的对话消息")
        conversations = Message.query.filter(
            Message.task_id == task_id,
            (
                (Message.sender_id == current_user.id) | 
                (Message.recipient_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).all()
        current_app.logger.info(f"获取到 {len(conversations)} 条对话消息")
        
        # 整理对话数据，按照对话对象分组
        current_app.logger.info(f"开始整理对话数据")
        conversations_by_user = {}
        for msg in conversations:
            try:
                other_user_id = msg.sender_id if msg.recipient_id == current_user.id else msg.recipient_id
                if other_user_id not in conversations_by_user:
                    other_user = User.query.get(other_user_id)
                    if not other_user:
                        current_app.logger.error(f"无法找到用户ID为 {other_user_id} 的用户")
                        continue
                    
                    conversations_by_user[other_user_id] = {
                        'id': f"{min(current_user.id, other_user_id)}_{max(current_user.id, other_user_id)}",  # 使用格式化的对话ID
                        'pro_name': other_user.username,
                        'pro_avatar': other_user.avatar_url or url_for('static', filename='images/default-avatar.jpg'),
                        'messages': [],
                        'has_unread': False,
                        'unread_count': 0,
                        'last_message_time': None,
                        'last_message_preview': ''
                    }
                
                # 添加消息到对话中
                conversations_by_user[other_user_id]['messages'].append(msg)
                
                # 检查是否有未读消息
                if msg.recipient_id == current_user.id and not msg.is_read:
                    conversations_by_user[other_user_id]['has_unread'] = True
                    conversations_by_user[other_user_id]['unread_count'] += 1
                
                # 更新最新消息时间和预览
                if not conversations_by_user[other_user_id]['last_message_time'] or \
                   msg.created_at > conversations_by_user[other_user_id]['last_message_time']:
                    conversations_by_user[other_user_id]['last_message_time'] = msg.created_at
                    # 限制消息预览长度并添加省略号
                    if len(msg.content) > 30:
                        conversations_by_user[other_user_id]['last_message_preview'] = msg.content[:30] + "..."
                    else:
                        conversations_by_user[other_user_id]['last_message_preview'] = msg.content
            except Exception as msg_e:
                current_app.logger.error(f"处理消息ID {msg.id}时出错: {str(msg_e)}")
        
        current_app.logger.info(f"对话数据整理完成，共有 {len(conversations_by_user)} 个对话")
        
        # 将对话按照最新消息时间排序
        conversations_list = sorted(
            conversations_by_user.values(),
            key=lambda x: x['last_message_time'] or datetime.min.isoformat(),
            reverse=True
        )
        
        # 查询对此任务感兴趣的专业人士
        current_app.logger.info(f"开始查询感兴趣的专业人士")
        interested_pros = []
        for user_id in conversations_by_user:
            try:
                user = User.query.get(user_id)
                if user and user.id != current_user.id:
                    # 获取完成的任务数量
                    completed_jobs = Task.query.filter(
                        (Task.executor_id == user.id) & 
                        (Task.status == 2)  # 假设状态2表示已完成
                    ).count()
                    
                    # 获取用户评分
                    reviews = Review.query.filter_by(reviewee_id=user.id).all()
                    rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
                    
                    interested_pros.append({
                        'id': user.id,
                        'name': user.username,
                        'avatar': user.avatar_url or url_for('static', filename='images/default-avatar.jpg'),
                        'rating': round(rating, 1),
                        'completed_jobs': completed_jobs
                    })
            except Exception as pro_e:
                current_app.logger.error(f"处理专业人士 {user_id} 数据时出错: {str(pro_e)}")
        
        current_app.logger.info(f"共找到 {len(interested_pros)} 个感兴趣的专业人士")
        
        # 模拟符合要求的专业人士数据
        current_app.logger.info(f"开始生成匹配的专业人士数据")
        matching_pros = []
        try:
            potential_pros = User.query.filter(User.id != current_user.id).limit(5).all()
            for user in potential_pros:
                # 获取用户评分
                reviews = Review.query.filter_by(reviewee_id=user.id).all()
                rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
                
                # 模拟匹配度和距离数据
                import random
                match_score = random.randint(70, 99)
                distance = round(random.uniform(0.5, 15.0), 1)
                
                matching_pros.append({
                    'id': user.id,
                    'name': user.username,
                    'avatar': user.avatar_url or url_for('static', filename='images/default-avatar.jpg'),
                    'rating': round(rating, 1),
                    'match_score': match_score,
                    'distance': distance
                })
            
            # 按匹配度排序
            matching_pros = sorted(matching_pros, key=lambda x: x['match_score'], reverse=True)
            current_app.logger.info(f"生成了 {len(matching_pros)} 个匹配的专业人士数据")
        except Exception as match_e:
            current_app.logger.error(f"生成匹配专业人士数据时出错: {str(match_e)}")
        
        # 准备渲染模板
        current_app.logger.info(f"准备渲染任务回应页面模板")
        try:
            unread_count = sum(conv['unread_count'] for conv in conversations_list)
            interested_count = len(interested_pros)
            matching_count = len(matching_pros)
            current_app.logger.info(f"未读消息数: {unread_count}, 感兴趣专业人士数: {interested_count}, 匹配专业人士数: {matching_count}")
            
            # 从会话中获取CSRF令牌
            from flask import session
            csrf_token = session.get('csrf_token', '')
            current_app.logger.info(f"CSRF令牌: {csrf_token[:10]}...")

            # 获取当前时间用于日期格式化
            now = datetime.now()
            
            return render_template('task_responses.html', 
                               task=task,
                               conversations=conversations_list,
                               interested_pros=interested_pros,
                               matching_pros=matching_pros,
                               unread_messages_count=unread_count,
                               interested_pros_count=interested_count,
                               matching_pros_count=matching_count,
                               csrf_token=csrf_token,
                               now=now)
        except Exception as render_e:
            current_app.logger.error(f"渲染模板时出错: {str(render_e)}, 错误类型: {type(render_e).__name__}")
            raise
    
    except Exception as e:
        current_app.logger.error(f"处理任务回应页面时发生错误: {str(e)}, 错误类型: {type(e).__name__}")
        import traceback
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        flash('加载任务回应页面时发生错误', 'danger')
        return redirect(url_for('task.tasks'))

@task_bp.route('/api/conversations/<int:other_user_id>/messages')
@login_required
def get_conversation_messages(other_user_id):
    """获取与特定用户的对话消息"""
    try:
        task_id = request.args.get('task_id')
        if not task_id:
            # 尝试从消息中获取任务ID
            message = Message.query.filter(
                ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
                ((Message.recipient_id == current_user.id) & (Message.sender_id == other_user_id))
            ).first()
            if message:
                task_id = message.task_id
            else:
                return jsonify({"error": "无法确定任务ID"}), 400
        
        # 查询与特定用户在特定任务下的所有消息
        messages = Message.query.filter(
            (Message.task_id == task_id) &
            (
                ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
                ((Message.recipient_id == current_user.id) & (Message.sender_id == other_user_id))
            )
        ).order_by(Message.created_at.asc()).all()
        
        # 计算未读消息数量
        unread_count = sum(1 for m in messages if m.recipient_id == current_user.id and not m.is_read)
        
        # 将消息转换为JSON格式
        messages_json = [{
            'id': m.id,
            'content': m.content,
            'sender_id': m.sender_id,
            'recipient_id': m.recipient_id,
            'created_at': m.created_at.isoformat(),
            'is_read': m.is_read
        } for m in messages]
        
        return jsonify({
            "messages": messages_json,
            "unread_count": unread_count,
            "task_id": task_id
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_conversation_messages: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/conversations/<int:other_user_id>/read', methods=['POST'])
@login_required
def mark_conversation_as_read(other_user_id):
    """将与特定用户的对话标记为已读"""
    try:
        task_id = request.args.get('task_id')
        if not task_id:
            return jsonify({"error": "任务ID不能为空"}), 400
            
        # 查找特定任务下，由other_user_id发送给当前用户的未读消息
        unread_messages = Message.query.filter(
            (Message.task_id == task_id) &
            (Message.sender_id == other_user_id) &
            (Message.recipient_id == current_user.id) &
            (Message.is_read == False)
        ).all()
        
        # 标记为已读
        for message in unread_messages:
            message.is_read = True
        
        db.session.commit()
        
        return jsonify({"success": True, "marked_count": len(unread_messages)})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in mark_conversation_as_read: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/professionals/<int:user_id>')
@login_required
def get_professional_details(user_id):
    """获取专业人士的详细信息"""
    try:
        current_app.logger.info(f"开始获取专业人士详情，用户ID: {user_id}")
        user = User.query.get_or_404(user_id)
        current_app.logger.info(f"找到用户: {user.username}, 头像URL: {user.avatar_url}")
        
        # 获取用户已完成的任务数量
        completed_jobs = Task.query.filter(
            (Task.executor_id == user.id) & 
            (Task.status == 2)  # 假设状态2表示已完成
        ).count()
        current_app.logger.info(f"用户已完成任务数: {completed_jobs}")
        
        # 获取用户评分
        reviews = Review.query.filter_by(reviewee_id=user.id).all()
        rating = sum([r.rating for r in reviews]) / len(reviews) if reviews else 0
        current_app.logger.info(f"用户评分: {rating}, 评论数: {len(reviews)}")
        
        # 获取用户技能 (假设用户模型有skills字段或关联表)
        skills = []
        if user.skills:
            skills = user.skills.split(',')
            current_app.logger.info(f"用户技能: {skills}")
        else:
            # 模拟一些技能
            from app.utils.constants import SERVICE_CATEGORIES
            import random
            all_services = []
            for category in SERVICE_CATEGORIES:
                all_services.extend([service[1] for service in category[1]])
            skills = random.sample(all_services, min(5, len(all_services)))
            current_app.logger.info(f"模拟的用户技能: {skills}")
        
        # 格式化评论
        reviews_json = []
        for review in reviews:
            reviewer = User.query.get(review.reviewer_id)
            if reviewer:
                reviews_json.append({
                    'id': review.id,
                    'rating': review.rating,
                    'content': review.content,
                    'reviewer_id': reviewer.id,
                    'reviewer_name': reviewer.username,
                    'created_at': review.created_at.isoformat() if hasattr(review, 'created_at') else None
                })
        
        # 构建响应
        response_data = {
            'id': user.id,
            'name': user.username,
            'avatar': user.avatar_url or url_for('static', filename='images/default-avatar.jpg'),
            'bio': user.bio or '',
            'profession': user.professional_title or '专业人士',
            'contact': user.phone or '未提供联系方式',
            'rating': round(rating, 1),
            'completed_jobs': completed_jobs,
            'skills': skills,
            'reviews': reviews_json
        }
        current_app.logger.info(f"返回专业人士详情: {response_data}")
        return jsonify(response_data)
    except Exception as e:
        current_app.logger.error(f"获取专业人士详情出错: {str(e)}")
        import traceback
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/<int:task_id>/hire/<int:pro_id>', methods=['POST'])
@login_required
def hire_professional(task_id, pro_id):
    """雇佣专业人士执行任务"""
    try:
        task = Task.query.get_or_404(task_id)
        pro = User.query.get_or_404(pro_id)
        
        # 检查权限
        if task.user_id != current_user.id:
            return jsonify({"success": False, "message": "您无权雇佣专业人士执行此任务"}), 403
        
        # 检查任务状态
        if task.status != 0:  # 假设0表示等待接单
            return jsonify({"success": False, "message": "该任务已不在等待接单状态"}), 400
        
        # 更新任务状态和执行者
        task.status = 1  # 假设1表示等待执行
        task.executor_id = pro_id
        db.session.commit()
        
        # 发送通知消息给专业人士
        message = Message(
            content=f"恭喜！您已被选中执行任务：{task.title}",
            sender_id=current_user.id,
            recipient_id=pro_id,
            task_id=task_id,
            created_at=datetime.utcnow()
        )
        db.session.add(message)
        db.session.commit()
        
        return jsonify({"success": True, "message": "已成功雇佣专业人士"})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in hire_professional: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/csrf-token')
@login_required
def get_csrf_token():
    """获取CSRF令牌的API端点"""
    try:
        from flask import session
        from flask_wtf.csrf import generate_csrf
        
        # 生成CSRF令牌
        csrf_token = generate_csrf()
        session['csrf_token'] = csrf_token
        
        return jsonify({"csrf_token": csrf_token})
    except Exception as e:
        current_app.logger.error(f"Error in get_csrf_token: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/conversations/<int:recipient_id>/messages', methods=['POST'])
@login_required
def send_conversation_message(recipient_id):
    """发送消息给特定用户"""
    try:
        # 获取请求数据
        data = request.get_json()
        if not data:
            return jsonify({"error": "无效的请求数据"}), 400
        
        content = data.get('content')
        task_id = data.get('task_id')
        
        if not content or not task_id:
            return jsonify({"error": "消息内容和任务ID不能为空"}), 400
        
        # 创建新消息
        message = Message(
            content=content,
            sender_id=current_user.id,
            recipient_id=recipient_id,
            task_id=task_id,
            created_at=datetime.utcnow(),
            is_read=False
        )
        
        db.session.add(message)
        db.session.commit()
        
        # 返回成功响应
        return jsonify({
            "success": True,
            "message": {
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender_id,
                'recipient_id': message.recipient_id,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in send_conversation_message: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/users/me/unread_messages')
@login_required
def get_unread_messages_count():
    """获取当前用户的未读消息数量"""
    try:
        # 查询当前用户的所有未读消息
        unread_count = Message.query.filter(
            (Message.recipient_id == current_user.id) & 
            (Message.is_read == False)
        ).count()
        
        return jsonify({
            "unread_count": unread_count
        })
    except Exception as e:
        current_app.logger.error(f"Error in get_unread_messages_count: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/conversations/with_professional/<int:pro_id>', methods=['POST'])
@login_required
def create_or_get_conversation(pro_id):
    """创建或获取与专业人士的对话"""
    try:
        task_id = request.args.get('task_id')
        if not task_id:
            return jsonify({"error": "任务ID不能为空"}), 400
        
        # 检查任务是否存在
        task = Task.query.get_or_404(task_id)
        
        # 检查当前用户是否为任务创建者
        if task.user_id != current_user.id:
            return jsonify({"error": "您无权为此任务创建对话"}), 403
        
        # 检查专业人士是否存在
        pro = User.query.get_or_404(pro_id)
        
        # 创建一条初始消息（如果没有现有对话）
        existing_message = Message.query.filter(
            (Message.task_id == task_id) &
            (
                ((Message.sender_id == current_user.id) & (Message.recipient_id == pro_id)) |
                ((Message.recipient_id == current_user.id) & (Message.sender_id == pro_id))
            )
        ).first()
        
        if not existing_message:
            # 创建初始消息
            message = Message(
                content=f"您好，我对您完成我的任务\"{task.title}\"感兴趣。",
                sender_id=current_user.id,
                recipient_id=pro_id,
                task_id=task_id,
                created_at=datetime.utcnow(),
                is_read=False
            )
            
            db.session.add(message)
            db.session.commit()
        
        # 返回对话ID（实际上是专业人士的ID）
        return jsonify({
            "success": True,
            "id": pro_id
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error in create_or_get_conversation: {str(e)}")
        return jsonify({"error": str(e)}), 500

@task_bp.route('/api/tasks/<task_id>/conversations')
@login_required
@csrf.exempt
def task_conversations(task_id):
    """获取与任务相关的所有对话"""
    try:
        # 检查任务是否存在
        task = Task.query.get_or_404(task_id)
        
        # 检查当前用户是否为任务创建者
        if task.user_id != current_user.id and not current_user.is_admin:
            return jsonify({"error": "您无权查看此任务的对话"}), 403
        
        # 获取与此任务相关的所有消息
        messages = Message.query.filter(
            Message.task_id == task_id,
            (
                (Message.sender_id == current_user.id) | 
                (Message.recipient_id == current_user.id)
            )
        ).order_by(Message.created_at.desc()).all()
        
        # 按用户分组消息
        conversations = {}
        for message in messages:
            other_user_id = message.sender_id if message.sender_id != current_user.id else message.recipient_id
            
            if other_user_id not in conversations:
                other_user = User.query.get(other_user_id)
                if not other_user:
                    continue
                
                # 创建对话ID (smaller_id_larger_id)
                conversation_id = f"{min(current_user.id, other_user_id)}_{max(current_user.id, other_user_id)}"
                
                conversations[other_user_id] = {
                    "id": conversation_id,
                    "other_user": {
                        "id": other_user_id,
                        "name": other_user.username,
                        "avatar": other_user.avatar_url or url_for('static', filename='images/default-avatar.jpg')
                    },
                    "messages": [],
                    "unread_count": 0,
                    "last_message_time": None,
                    "last_message_preview": ""
                }
            
            # 添加消息到对话
            conversations[other_user_id]["messages"].append({
                "id": message.id,
                "content": message.content,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "created_at": message.created_at.isoformat(),
                "is_read": message.is_read
            })
            
            # 更新最后消息时间
            if not conversations[other_user_id]["last_message_time"] or message.created_at > conversations[other_user_id]["last_message_time"]:
                conversations[other_user_id]["last_message_time"] = message.created_at
                # 限制消息预览长度并添加省略号
                if len(message.content) > 30:
                    conversations[other_user_id]["last_message_preview"] = message.content[:30] + "..."
                else:
                    conversations[other_user_id]["last_message_preview"] = message.content
            
            # 计算未读消息数
            if message.recipient_id == current_user.id and not message.is_read:
                conversations[other_user_id]["unread_count"] += 1
        
        # 转换为列表并按最后消息时间排序
        conversation_list = list(conversations.values())
        conversation_list.sort(key=lambda x: x["last_message_time"] or datetime.min, reverse=True)
        
        # 添加调试日志
        current_app.logger.info(f"找到 {len(conversation_list)} 个对话")
        for conv in conversation_list:
            current_app.logger.info(f"对话ID: {conv['id']}, 用户: {conv['other_user']['name']}, 未读消息: {conv['unread_count']}")
        
        return jsonify({
            "task_id": task_id,
            "conversations": conversation_list
        })
    
    except Exception as e:
        current_app.logger.error(f"获取任务对话出错: {str(e)}")
        return jsonify({"error": "获取对话失败"}), 500

# 添加调试路由
@task_bp.route('/debug/task/<task_id>/messages')
@login_required
def debug_task_messages(task_id):
    """调试路由：查看与任务相关的所有消息"""
    try:
        task = Task.query.get_or_404(task_id)
        
        # 获取与此任务相关的所有消息
        messages = Message.query.filter_by(task_id=task_id).all()
        
        result = []
        for msg in messages:
            sender = User.query.get(msg.sender_id)
            recipient = User.query.get(msg.recipient_id)
            
            result.append({
                'id': msg.id,
                'sender': {
                    'id': sender.id,
                    'name': sender.username
                },
                'recipient': {
                    'id': recipient.id,
                    'name': recipient.username
                },
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read
            })
        
        # 按照对话对象分组
        conversations = {}
        for msg in messages:
            user_pair = tuple(sorted([msg.sender_id, msg.recipient_id]))
            if user_pair not in conversations:
                user1 = User.query.get(user_pair[0])
                user2 = User.query.get(user_pair[1])
                
                conversations[user_pair] = {
                    'id': f"{user_pair[0]}_{user_pair[1]}",
                    'user1': {
                        'id': user1.id,
                        'name': user1.username
                    },
                    'user2': {
                        'id': user2.id,
                        'name': user2.username
                    },
                    'created_at': msg.created_at.isoformat()
                }
        
        return jsonify({
            'task': {
                'id': task.id,
                'title': task.title,
                'user_id': task.user_id
            },
            'messages_count': len(messages),
            'messages': result,
            'conversations_count': len(conversations),
            'conversations': list(conversations.values())
        })
    except Exception as e:
        current_app.logger.error(f"调试任务消息时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 获取任务推荐用户的辅助函数
def get_recommended_users_for_task(task):
    try:
        # 获取感兴趣的用户（发送过消息的用户）
        interested_users = set()
        for message in task.messages:
            if message.sender_id != task.author.id:
                interested_users.add(message.sender)
        
        # 获取平台推荐用户（只推荐专业人士）
        # 1. 只选择已注册为专业人士的用户
        # 2. 排除任务发布者自己
        # 3. 优先推荐与任务类别匹配的专业人士
        if task.service_category:
            main_cat, sub_cat = task.service_category.split('.')
            category_id = task.service_category
            
            # 查找与任务类别匹配的专业人士
            matching_pros = User.query.join(UserCategory).filter(
                User.is_professional == True,
                User.id != task.author.id,
                UserCategory.category_id == category_id
            ).all()
            
            # 如果匹配的专业人士不足5人，再查找同一主类别下的专业人士
            if len(matching_pros) < 5:
                more_pros = User.query.join(UserCategory).filter(
                    User.is_professional == True,
                    User.id != task.author.id,
                    UserCategory.category_id.like(f"{main_cat}.%"),
                    ~User.id.in_([pro.id for pro in matching_pros])
                ).limit(5 - len(matching_pros)).all()
                
                matching_pros.extend(more_pros)
            
            # 如果仍然不足5人，再随机推荐其他专业人士
            if len(matching_pros) < 5:
                random_pros = User.query.filter(
                    User.is_professional == True,
                    User.id != task.author.id,
                    ~User.id.in_([pro.id for pro in matching_pros])
                ).order_by(db.func.random()).limit(5 - len(matching_pros)).all()
                
                matching_pros.extend(random_pros)
            
            recommended_users = matching_pros
        else:
            # 如果任务没有指定类别，随机推荐专业人士
            recommended_users = User.query.filter(
                User.is_professional == True,
                User.id != task.author.id
            ).order_by(db.func.random()).limit(5).all()
            
        # 计算任务的响应数量（不同的消息发送者数量）
        senders = set()
        for message in task.messages:
            if message.sender_id != task.author.id:
                senders.add(message.sender_id)
        responses_count = len(senders)
        
        # 将responses_count添加到task对象中，以便在模板中使用
        task.responses_count = responses_count
        
        # 为推荐用户添加匹配分数
        for user in recommended_users:
            if hasattr(user, 'average_rating') and user.average_rating:
                rating_score = min(user.average_rating * 10, 50)  # 最高贡献50分
            else:
                rating_score = 0
                
            # 计算完成任务的匹配分数
            completed_tasks_score = min(user.completed_tasks * 5, 30)  # 最高贡献30分
            
            # 类别匹配分数
            category_match_score = 0
            if category_id and user.has_category(category_id):
                category_match_score = 20  # 精确匹配贡献20分
            
            # 计算总分
            user.match_score = int(rating_score + completed_tasks_score + category_match_score)
            
        # 按匹配分数排序
        recommended_users = sorted(recommended_users, key=lambda x: x.match_score, reverse=True)
        
        return recommended_users
    except Exception as e:
        current_app.logger.error(f"获取推荐用户时出错: {str(e)}")
        return [] 