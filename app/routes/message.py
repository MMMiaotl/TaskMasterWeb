from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify, current_app
from flask_login import current_user, login_required
from app import db, csrf
from app.models import Message, User, Task
from app.forms import MessageForm
from datetime import datetime

message_bp = Blueprint('message', __name__, url_prefix='')

@message_bp.route('/messages')
@message_bp.route('/messages/<int:user_id>')
@login_required
def messages(user_id=None):
    # 获取当前用户的所有对话
    all_messages = Message.query.filter(
        (Message.sender_id == current_user.id) | (Message.recipient_id == current_user.id)
    ).order_by(Message.created_at.desc()).all()
    
    # 按用户分组消息
    conversations = {}
    for message in all_messages:
        other_user_id = message.sender_id if message.sender_id != current_user.id else message.recipient_id
        
        if other_user_id not in conversations:
            other_user = User.query.get(other_user_id)
            if not other_user:
                continue
                
            conversations[other_user_id] = {
                'user': other_user,
                'messages': [],
                'unread_count': 0,
                'last_message_time': None,
                'last_message_preview': '',
                'task': None
            }
        
        # 添加消息到对话
        conversations[other_user_id]['messages'].append(message)
        
        # 更新未读消息计数
        if message.recipient_id == current_user.id and not message.is_read:
            conversations[other_user_id]['unread_count'] += 1
            
        # 更新最后消息时间和预览
        if not conversations[other_user_id]['last_message_time'] or message.created_at > conversations[other_user_id]['last_message_time']:
            conversations[other_user_id]['last_message_time'] = message.created_at
            conversations[other_user_id]['last_message_preview'] = message.content[:50] + ('...' if len(message.content) > 50 else '')
            
            # 更新关联的任务
            if message.task_id and not conversations[other_user_id]['task']:
                conversations[other_user_id]['task'] = Task.query.get(message.task_id)
    
    # 对每个会话中的消息按时间排序
    for conv in conversations.values():
        conv['messages'] = sorted(conv['messages'], key=lambda x: x.created_at)
    
    # 如果指定了用户ID，则获取与该用户的对话
    selected_conversation = None
    selected_user_id = None
    if user_id and user_id in conversations:
        selected_conversation = conversations[user_id]
        selected_user_id = user_id
        
        # 标记消息为已读
        for message in selected_conversation['messages']:
            if message.recipient_id == current_user.id and not message.is_read:
                message.is_read = True
        db.session.commit()
    elif conversations:
        # 如果没有指定用户但有对话，默认选择最近的一个
        recent_user_id = max(conversations.items(), key=lambda x: x[1]['last_message_time'])[0]
        return redirect(url_for('message.messages', user_id=recent_user_id))
    
    return render_template('messages.html', 
                           conversations=conversations, 
                           selected_conversation=selected_conversation,
                           selected_user_id=selected_user_id)

@message_bp.route('/send_message/<int:recipient_id>', methods=['POST'])
@login_required
def send_message(recipient_id):
    # 确保接收者存在
    recipient = User.query.get_or_404(recipient_id)
    
    # 获取消息内容
    content = request.form.get('content')
    if not content:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'error': '消息内容不能为空'})
        flash('消息内容不能为空', 'danger')
        return redirect(url_for('message.messages', user_id=recipient_id))
    
    # 查找最近的消息以获取任务ID（如果有）
    recent_message = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.recipient_id == recipient_id)) |
        ((Message.recipient_id == current_user.id) & (Message.sender_id == recipient_id))
    ).order_by(Message.created_at.desc()).first()
    
    task_id = None
    if recent_message and recent_message.task_id:
        task_id = recent_message.task_id
    
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
    
    # 根据请求类型返回响应
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'content': message.content,
                'sender_id': message.sender_id,
                'recipient_id': message.recipient_id,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read
            },
            'current_user_name': current_user.username,
            'current_user_avatar': current_user.avatar_url or url_for('static', filename='images/default-avatar.jpg')
        })
    
    flash('消息已发送', 'success')
    return redirect(url_for('message.messages', user_id=recipient_id))

@message_bp.route('/send_message/<int:recipient_id>/<int:task_id>', methods=['POST'])
@login_required
def send_task_message(recipient_id, task_id):
    task = Task.query.get_or_404(task_id)
    if current_user.id not in [task.user_id, task.executor_id]:
        abort(403)
    
    form = MessageForm()
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=form.content.data,
            task_id=task_id
        )
        db.session.add(message)
        db.session.commit()
        flash('消息已发送')
    
    return redirect(url_for('task.task_conversation', task_id=task_id))

@message_bp.route('/user/messages')
@login_required
def user_messages():
    # 使用joinedload预加载关联数据
    sent_messages = Message.query.options(db.joinedload(Message.task))\
        .filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc())\
        .all()

    received_messages = Message.query.options(db.joinedload(Message.task))\
        .filter_by(recipient_id=current_user.id)\
        .order_by(Message.created_at.desc())\
        .all()

    return render_template('user_messages.html',
                         sent_messages=sent_messages,
                         received_messages=received_messages)

@message_bp.route('/message/<int:message_id>/respond_invitation', methods=['POST'])
@login_required
def respond_invitation(message_id):
    message = Message.query.get_or_404(message_id)
    task = message.task
    
    # 检查当前用户是否有权限响应邀请
    if message.recipient != current_user:
        flash('你没有权限响应此邀请', 'error')
        return redirect(url_for('message.user_messages'))
    
    # 检查任务状态
    if task.status != 0:
        flash('该任务已经有人接单', 'warning')
        return redirect(url_for('message.user_messages'))
    
    try:
        response = request.form.get('response')
        if response == 'accept':
            message.invitation_accepted = True
            task.status = 1  # 将任务状态改为"已接单"
            task.executor_id = current_user.id  # 设置任务执行者
            flash('你已成功接受任务', 'success')
        elif response == 'reject':
            message.invitation_accepted = False
            flash('你已拒绝任务邀请', 'info')
        else:
            flash('无效的响应', 'error')
            return redirect(url_for('message.user_messages'))
        
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('处理邀请时出错：' + str(e), 'error')
    
    return redirect(url_for('message.user_messages'))

@message_bp.route('/api/messages', methods=['GET'])
@login_required
@csrf.exempt
def get_messages():
    """获取与特定用户的消息"""
    try:
        other_user_id = request.args.get('other_user_id')
        task_id = request.args.get('task_id')
        
        current_app.logger.info(f"获取消息API: other_user_id={other_user_id}, task_id={task_id}, current_user_id={current_user.id}")
        
        if not other_user_id:
            current_app.logger.error("缺少other_user_id参数")
            return jsonify({'error': '缺少other_user_id参数'}), 400
            
        if not task_id:
            current_app.logger.error("缺少task_id参数")
            return jsonify({'error': '缺少task_id参数'}), 400
            
        # 尝试转换参数为整数
        try:
            other_user_id = int(other_user_id)
            task_id = int(task_id)
        except ValueError as e:
            current_app.logger.error(f"参数类型错误: {str(e)}")
            return jsonify({'error': f'参数类型错误: {str(e)}'}), 400
            
        # 检查用户是否存在
        other_user = User.query.get(other_user_id)
        if not other_user:
            current_app.logger.error(f"用户不存在: other_user_id={other_user_id}")
            # 返回空消息列表而不是404错误
            return jsonify({
                'messages': [],
                'unread_count': 0,
                'error_info': f'用户不存在: ID={other_user_id}'
            })
            
        # 检查任务是否存在
        task = Task.query.get(task_id)
        if not task:
            current_app.logger.error(f"任务不存在: task_id={task_id}")
            # 返回空消息列表而不是404错误
            return jsonify({
                'messages': [],
                'unread_count': 0,
                'error_info': f'任务不存在: ID={task_id}'
            })
        
        # 直接使用filter_by进行精确匹配，避免复杂的条件组合
        query = Message.query.filter(
            Message.task_id == task_id,
            (
                ((Message.sender_id == current_user.id) & (Message.recipient_id == other_user_id)) |
                ((Message.recipient_id == current_user.id) & (Message.sender_id == other_user_id))
            )
        )
        
        # 打印SQL查询语句
        current_app.logger.info(f"SQL查询: {str(query)}")
        
        # 查询消息
        messages = query.order_by(Message.created_at.asc()).all()
        
        current_app.logger.info(f"找到 {len(messages)} 条消息")
        for i, msg in enumerate(messages[:3]):  # 只记录前3条消息
            current_app.logger.info(f"消息 {i+1}: sender_id={msg.sender_id}, recipient_id={msg.recipient_id}, content={msg.content[:30]}...")
        
        # 计算未读消息数
        unread_count = Message.query.filter(
            Message.task_id == task_id,
            Message.recipient_id == current_user.id,
            Message.sender_id == other_user_id,
            Message.is_read == False
        ).count()
        
        current_app.logger.info(f"未读消息数: {unread_count}")
        
        # 转换为JSON格式
        messages_json = []
        for msg in messages:
            messages_json.append({
                'id': msg.id,
                'sender_id': msg.sender_id,
                'recipient_id': msg.recipient_id,
                'content': msg.content,
                'created_at': msg.created_at.isoformat(),
                'is_read': msg.is_read
            })
        
        current_app.logger.info(f"返回 {len(messages_json)} 条消息")
        
        return jsonify({
            'messages': messages_json,
            'unread_count': unread_count
        })
    except Exception as e:
        current_app.logger.error(f"获取消息时出错: {str(e)}")
        import traceback
        current_app.logger.error(f"错误堆栈: {traceback.format_exc()}")
        # 返回一个友好的错误信息和空消息列表
        return jsonify({
            'messages': [],
            'unread_count': 0,
            'error_info': f'获取消息出错: {str(e)}'
        })

@message_bp.route('/api/messages/mark_read', methods=['POST'])
@login_required
@csrf.exempt
def mark_messages_read():
    """标记与特定用户和任务相关的消息为已读"""
    try:
        # 尝试从JSON请求体获取数据
        data = request.get_json()
        if data:
            other_user_id = data.get('other_user_id')
            task_id = data.get('task_id')
        else:
            # 回退到URL参数
            other_user_id = request.args.get('other_user_id')
            task_id = request.args.get('task_id')
        
        current_app.logger.debug(f"标记消息为已读：other_user_id={other_user_id}, task_id={task_id}")
        
        if not other_user_id:
            return jsonify({'error': '缺少other_user_id参数'}), 400
        
        # 构建查询条件
        conditions = [
            Message.recipient_id == current_user.id,
            Message.sender_id == other_user_id,
            Message.is_read == False
        ]
        
        # 如果提供了任务ID，添加任务过滤条件
        if task_id:
            conditions.append(Message.task_id == task_id)
        
        # 查询未读消息
        unread_messages = Message.query.filter(*conditions).all()
        
        # 标记为已读
        for msg in unread_messages:
            msg.is_read = True
        
        # 提交更改
        db.session.commit()
        
        return jsonify({
            'success': True,
            'marked_count': len(unread_messages)
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"标记消息为已读时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/api/messages/send', methods=['POST'])
@login_required
@csrf.exempt
def api_send_message():
    """API接口 - 发送消息"""
    try:
        data = request.get_json()
        
        recipient_id = data.get('recipient_id')
        content = data.get('content')
        task_id = data.get('task_id')
        
        if not recipient_id or not content:
            return jsonify({'error': '缺少必要参数'}), 400
            
        # 记录调试信息
        current_app.logger.info(f"发送消息: recipient_id={recipient_id}, task_id={task_id}, content={content[:20]}...")
        
        # 创建新消息
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=content,
            task_id=task_id,
            is_read=False
        )
        
        # 保存消息
        db.session.add(message)
        db.session.commit()
        
        current_app.logger.info(f"消息发送成功: message_id={message.id}")
        
        return jsonify({
            'success': True,
            'message': {
                'id': message.id,
                'sender_id': message.sender_id,
                'recipient_id': message.recipient_id,
                'content': message.content,
                'created_at': message.created_at.isoformat(),
                'is_read': message.is_read,
                'task_id': message.task_id
            }
        })
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"发送消息时出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

@message_bp.route('/api/users/me/unread_messages')
@login_required
@csrf.exempt
def get_unread_messages_count():
    """获取当前用户的未读消息数量"""
    try:
        # 查询当前用户的所有未读消息
        unread_count = Message.query.filter_by(
            recipient_id=current_user.id,
            is_read=False
        ).count()
        
        return jsonify({
            "unread_count": unread_count
        })
    except Exception as e:
        current_app.logger.error(f"获取未读消息数失败: {str(e)}")
        return jsonify({"error": "获取未读消息数失败", "error_info": str(e)}), 500