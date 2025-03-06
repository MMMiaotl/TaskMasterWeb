from flask import Blueprint, render_template, flash, redirect, url_for, request, abort, jsonify, current_app
from flask_login import current_user, login_required
from app import db, csrf
from app.models import Message, User, Task
from app.forms import MessageForm

message_bp = Blueprint('message', __name__, url_prefix='')

@message_bp.route('/messages')
@login_required
def messages():
    received = Message.query.filter_by(recipient_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    sent = Message.query.filter_by(sender_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    return render_template('messages.html', received_messages=received, sent_messages=sent)

@message_bp.route('/send_message/<int:recipient_id>', methods=['GET', 'POST'])
@message_bp.route('/send_message/<int:recipient_id>/<int:task_id>', methods=['GET', 'POST'])
@login_required
def send_message(recipient_id, task_id=None):
    recipient = User.query.get_or_404(recipient_id)
    task = Task.query.get(task_id) if task_id else None
    form = MessageForm()
    
    if form.validate_on_submit():
        message = Message(
            sender_id=current_user.id,
            recipient_id=recipient_id,
            content=form.content.data,
            task_id=task_id if task_id else None
        )
        db.session.add(message)
        db.session.commit()
        flash('消息已发送')
        return redirect(url_for('message.messages'))
    
    return render_template('send_message.html', 
                         form=form, 
                         recipient=recipient,
                         task=task)

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