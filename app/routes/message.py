from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app import db
from app.models import Message, Task
from app.forms import MessageForm

message_bp = Blueprint('message', __name__)

@message_bp.route('/messages')
@login_required
def messages():
    messages = Message.query.filter_by(recipient_id=current_user.id)\
        .order_by(Message.created_at.desc()).all()
    return render_template('messages.html', messages=messages)

@message_bp.route('/task/<int:task_id>/send_message', methods=['POST'])
@login_required
def send_message(task_id):
    task = Task.query.get_or_404(task_id)
    form = MessageForm()

    if form.validate_on_submit():
        message = Message(
            content=form.content.data,
            sender_id=current_user.id,
            recipient_id=task.user_id,
            task_id=task.id
        )
        db.session.add(message)
        db.session.commit()
        flash('Your message has been sent!', 'success')
    else:
        flash('Failed to send message. Please check the form.', 'danger')

    return redirect(url_for('task.task_detail', task_id=task.id)) 