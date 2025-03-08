from flask import Blueprint, render_template, flash, redirect, url_for, request, current_app
from flask_login import login_user, logout_user, current_user
from urllib.parse import urlparse
from app import db
from app.models import User
from app.forms import LoginForm, RegistrationForm, ProfessionalLoginForm, ProfessionalRegistrationForm
from app.utils.email import send_confirmation_email
from datetime import datetime

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
            
            # 检查邮箱是否已验证
            if not user.email_confirmed:
                flash('您的邮箱尚未验证，请先验证邮箱')
                return redirect(url_for('auth.login', resend=user.id))
            
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or urlparse(next_page).netloc != '':
                next_page = url_for('main.index')
            return redirect(next_page)
        
        # 如果有resend参数，显示重新发送验证邮件的选项
        resend_user_id = request.args.get('resend')
        return render_template('login.html', title='登录', form=form, resend_user_id=resend_user_id)
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
            print(f"===== 注册表单提交 =====")
            print(f"用户名: {form.username.data}")
            print(f"邮箱: {form.email.data}")
            
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                flash('该邮箱已被注册')
                return redirect(url_for('auth.register'))
            
            user = User(
                username=form.username.data, 
                email=form.email.data,
                email_confirmed=False
            )
            user.set_password(form.password.data)
            
            # 生成邮箱验证令牌
            token = user.generate_email_token()
            print(f"生成的验证令牌: {token}")
            
            # 保存用户
            db.session.add(user)
            db.session.commit()
            print(f"用户已保存到数据库，ID: {user.id}")
            
            # 发送确认邮件
            print(f"===== 开始发送确认邮件 =====")
            try:
                send_confirmation_email(user, token)
                print(f"===== 确认邮件发送完成 =====")
            except Exception as e:
                print(f"===== 发送确认邮件时出错: {str(e)} =====")
                import traceback
                traceback.print_exc()
            
            flash('注册成功！请查看您的邮箱并点击确认链接完成注册。')
            return redirect(url_for('auth.login'))
        
        return render_template('register.html', title='注册', form=form)
    except Exception as e:
        db.session.rollback()
        print(f"===== 注册过程中发生错误: {str(e)} =====")
        import traceback
        traceback.print_exc()
        flash(f'注册过程中发生错误: {str(e)}')
        return redirect(url_for('auth.register'))

@auth_bp.route('/confirm/<token>')
def confirm_email(token):
    try:
        if current_user.is_authenticated and current_user.email_confirmed:
            flash('您的账号已经验证过了')
            return redirect(url_for('main.index'))
        
        # 查找具有此令牌的用户
        user = User.query.filter_by(email_confirm_token=token).first()
        
        if not user:
            flash('无效的验证链接或链接已过期')
            return redirect(url_for('auth.login'))
        
        # 检查令牌是否过期
        if user.token_expired(expiration=86400):  # 24小时过期
            flash('验证链接已过期，请重新注册或联系管理员')
            return redirect(url_for('auth.login'))
        
        # 确认邮箱
        if user.confirm_email(token):
            db.session.commit()
            flash('邮箱验证成功！现在您可以登录了。')
        else:
            flash('验证失败，请重试或联系管理员')
        
        return redirect(url_for('auth.login'))
    except Exception as e:
        db.session.rollback()
        flash(f'验证过程中发生错误: {str(e)}')
        return redirect(url_for('auth.login'))

@auth_bp.route('/resend_confirmation')
def resend_confirmation():
    try:
        if not current_user.is_authenticated:
            flash('请先登录')
            return redirect(url_for('auth.login'))
        
        if current_user.email_confirmed:
            flash('您的邮箱已经验证过了')
            return redirect(url_for('main.index'))
        
        # 生成新的令牌
        token = current_user.generate_email_token()
        db.session.commit()
        
        # 发送确认邮件
        send_confirmation_email(current_user, token)
        
        flash('验证邮件已重新发送，请查收')
        return redirect(url_for('main.index'))
    except Exception as e:
        db.session.rollback()
        flash(f'发送验证邮件时发生错误: {str(e)}')
        return redirect(url_for('main.index'))

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

@auth_bp.route('/test_real_email/<email>')
def test_real_email(email):
    try:
        print(f"===== 测试发送真实邮件到 {email} =====")
        
        # 创建一个测试用户
        test_user = User(
            username="测试用户",
            email=email,
            email_confirmed=False
        )
        
        # 生成令牌
        token = "test_token_" + str(datetime.utcnow().timestamp())
        print(f"测试令牌: {token}")
        
        # 发送确认邮件
        try:
            send_confirmation_email(test_user, token)
            print(f"===== 测试邮件发送成功 =====")
            return f"测试邮件已发送到 {email}，请检查您的邮箱"
        except Exception as e:
            print(f"===== 发送测试邮件时出错: {str(e)} =====")
            import traceback
            traceback.print_exc()
            return f"发送测试邮件失败: {str(e)}"
    except Exception as e:
        print(f"===== 测试路由中发生错误: {str(e)} =====")
        import traceback
        traceback.print_exc()
        return f"测试过程中发生错误: {str(e)}" 