from flask import render_template, flash, redirect, url_for, request, session
from flask_login import login_user, logout_user, current_user, login_required
from app import app, db
from app.models import User, Task, Review
from app.forms import LoginForm, RegistrationForm, TaskForm
from flask_babel import gettext as _

@app.route('/')
def index():
    search_query = request.args.get('q', '')  # 获取搜索关键词
    if search_query:
        tasks = Task.query.filter(Task.title.contains(search_query) | Task.description.contains(search_query)).all()
    else:
        tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        # 检查邮箱是否已存在
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash('Email address is already registered.')
            return redirect(url_for('register'))
        
        # 创建新用户
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, description=form.description.data, user_id=current_user.id)
        db.session.add(task)
        db.session.commit()
        flash('Your task has been created!')
        return redirect(url_for('index'))
    return render_template('create_task.html', title='Create Task', form=form)

@app.route('/tasks')
@login_required
def tasks():
    search_query = request.args.get('q', '')  # 获取搜索关键词
    if search_query:
        tasks = Task.query.filter(Task.title.contains(search_query) | Task.description.contains(search_query)).all()
    else:
        tasks = Task.query.all()
    return render_template('tasks.html', tasks=tasks)

@app.route('/task/<int:task_id>')
def task_detail(task_id):
    task = Task.query.get_or_404(task_id)  # 获取任务，如果不存在则返回 404
    return render_template('task_detail.html', task=task)

@app.route('/task/<int:task_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    task = Task.query.get_or_404(task_id)  # 获取任务，如果不存在则返回 404
    if task.user_id != current_user.id:  # 确保当前用户是任务发布者
        flash('You do not have permission to edit this task.')
        return redirect(url_for('index'))

    form = TaskForm(obj=task)  # 使用任务数据填充表单
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        db.session.commit()
        flash('Task updated successfully!')
        return redirect(url_for('task_detail', task_id=task.id))

    return render_template('edit_task.html', form=form, task=task)  # 确保传递 task 变量

@app.route('/task/<int:task_id>/delete', methods=['POST'])
@login_required
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    if task.user_id != current_user.id:  # 确保当前用户是任务发布者
        flash('You do not have permission to delete this task.')
        return redirect(url_for('index'))

    db.session.delete(task)
    db.session.commit()
    flash('Task deleted successfully!')
    return redirect(url_for('index'))

@app.route('/set_language/<language>')
def set_language(language):
    if language in app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = language
    return redirect(request.referrer or url_for('index'))

@app.route('/user')
@login_required  # 确保只有登录用户才能访问
def user_profile():
    # 假设 current_user 包含用户信息
    user_info = {
        'username': current_user.username,
        'email': current_user.email,
    }
    return render_template('user_profile.html', user_info=user_info)

@app.route('/users/<username>')
def other_user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()  # 根据用户名查找用户，如果不存在则返回 404
    return render_template('other_user_profile.html', user=user)

@app.route('/task/<int:task_id>/review', methods=['GET', 'POST'])
@login_required
def create_review(task_id):
    task = Task.query.get_or_404(task_id)
    form = ReviewForm()

    # 确保当前用户是任务的发布人或执行人
    if current_user.id != task.user_id and current_user.id != task.executor_id:
        flash('You are not authorized to review this task.')
        return redirect(url_for('task_detail', task_id=task.id))

    if form.validate_on_submit():
        review = Review(
            content=form.content.data,
            rating=form.rating.data,
            reviewer_id=current_user.id,
            reviewee_id=task.user_id if form.role.data == 'poster' else task.executor_id,
            task_id=task.id,
            role=form.role.data
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!')
        return redirect(url_for('task_detail', task_id=task.id))

    return render_template('create_review.html', form=form, task=task)

@app.route('/user/<username>/reviews')
def user_reviews(username):
    user = User.query.filter_by(username=username).first_or_404()
    poster_reviews = Review.query.filter_by(reviewee_id=user.id, role='poster').all()  # 作为发布人收到的评价
    executor_reviews = Review.query.filter_by(reviewee_id=user.id, role='executor').all()  # 作为执行人收到的评价
    return render_template('user_reviews.html', user=user, poster_reviews=poster_reviews, executor_reviews=executor_reviews)