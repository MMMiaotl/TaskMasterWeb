from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm, ProfessionalLoginForm, ProfessionalRegistrationForm

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user is None or not user.check_password(form.password.data):
                flash('用户名或密码错误')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        
        return render_template('login.html', title='登录', form=form)
    except Exception as e:
        db.session.rollback()  # 回滚任何未完成的事务
        flash(f'登录过程中发生错误: {str(e)}')
        return redirect(url_for('auth.login'))

@auth_bp.route('/professional/login', methods=['GET', 'POST'])
def professional_login():
    try:
        if current_user.is_authenticated:
            if current_user.is_professional:
                return redirect(url_for('professional.dashboard'))
            else:
                flash('您不是专业人士，请使用普通用户登录')
                return redirect(url_for('auth.login'))
        
        form = ProfessionalLoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            
            if user is None or not user.check_password(form.password.data):
                flash('用户名或密码错误')
                return redirect(url_for('auth.professional_login'))
            
            if not user.is_professional:
                flash('此账户不是专业人士账户，请使用普通用户登录')
                return redirect(url_for('auth.login'))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('professional.dashboard')
            return redirect(next_page)
        
        return render_template('professional/login.html', title='专业人士登录', form=form)
    except Exception as e:
        db.session.rollback()
        flash(f'登录过程中发生错误: {str(e)}')
        return redirect(url_for('auth.professional_login'))

@auth_bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('该邮箱已被注册')
                return redirect(url_for('auth.register'))
            
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('注册成功！')
            return redirect(url_for('auth.login'))
        
        return render_template('register.html', title='注册', form=form)
    except Exception as e:
        db.session.rollback()  # 回滚任何未完成的事务
        flash(f'注册过程中发生错误: {str(e)}')
        return redirect(url_for('auth.register'))

@auth_bp.route('/professional/register', methods=['GET', 'POST'])
def professional_register():
    try:
        if current_user.is_authenticated:
            return redirect(url_for('main.index'))
        
        form = ProfessionalRegistrationForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('该邮箱已被注册')
                return redirect(url_for('auth.professional_register'))
            
            user = User(
                username=form.username.data, 
                email=form.email.data,
                is_professional=True,
                professional_title=form.professional_title.data,
                professional_summary=form.professional_summary.data,
                experience_years=form.experience_years.data,
                hourly_rate=form.hourly_rate.data,
                skills=form.skills.data,
                certifications=form.certifications.data,
                phone=form.phone.data,
                location=form.location.data
            )
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('专业人士注册成功！请登录您的账户。')
            return redirect(url_for('auth.professional_login'))
        
        return render_template('professional/register.html', title='专业人士注册', form=form)
    except Exception as e:
        db.session.rollback()
        flash(f'注册过程中发生错误: {str(e)}')
        return redirect(url_for('auth.professional_register')) 