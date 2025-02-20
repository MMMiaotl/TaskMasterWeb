from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.models import Task
from app.forms import TaskForm
from sqlalchemy import or_
from datetime import datetime
from app.utils.constants import SERVICE_CATEGORIES

task_bp = Blueprint('task', __name__)

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
    if form.validate_on_submit():
        try:
            task = Task(
                title=form.title.data,
                description=form.description.data,
                service_category=form.service_category.data,
                location=form.location.data,
                deadline=form.deadline.data,
                budget=form.budget.data,
                user_id=current_user.id
            )
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
                         categories=SERVICE_CATEGORIES)

@task_bp.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template('task_detail.html', task=task)

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