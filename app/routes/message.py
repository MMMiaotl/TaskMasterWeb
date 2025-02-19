from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.models import Message, User, Task
from app.forms import MessageForm

message_bp = Blueprint('message', __name__)

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
            task_id=task_id if task else None
        )
        db.session.add(message)
        db.session.commit()
        flash('消息已发送')
        return redirect(url_for('message.messages'))
    
    return render_template('send_message.html', 
                         form=form, 
                         recipient=recipient,
                         task=task) 