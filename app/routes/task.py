from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.models import Task
from app.forms import TaskForm, MessageForm

task_bp = Blueprint('task', __name__)

@task_bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, 
                   description=form.description.data, 
                   user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!')
        return redirect(url_for('main.index'))
    return render_template('create_task.html', title='Create Task', form=form)

@task_bp.route('/tasks')
@login_required
def tasks():
    search_query = request.args.get('q', '')
    if search_query:
        tasks = Task.query.filter(Task.title.contains(search_query) | 
                                Task.description.contains(search_query)).all()
    else:
        tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@task_bp.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    form = MessageForm()
    return render_template('task_detail.html', task=task, form=form)

@task_bp.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to edit this task.')
        return redirect(url_for('main.index'))

    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('task.task_detail', task_id=task.id))
    return render_template('edit_task.html', form=form, task=task)

@task_bp.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:
        flash('You do not have permission to delete this task.')
        return redirect(url_for('main.index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('main.index')) 