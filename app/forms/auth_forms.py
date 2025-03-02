from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from app.models import User

class LoginForm(FlaskForm):
    """用户登录表单"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    """用户注册表单"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')

    def validate_email(self, email):
        """验证邮箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱')

class ProfessionalLoginForm(FlaskForm):
    """专业人士登录表单"""
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('专业人士登录')

class ProfessionalRegistrationForm(FlaskForm):
    """专业人士注册表单，包含额外的专业信息"""
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    
    # 专业信息
    professional_title = StringField('职业头衔', validators=[DataRequired(), Length(max=64)])
    professional_summary = TextAreaField('专业简介', validators=[DataRequired(), Length(min=30, max=500)])
    experience_years = IntegerField('从业年限', validators=[DataRequired(), NumberRange(min=0, max=50)])
    hourly_rate = FloatField('每小时费率 (€)', validators=[DataRequired(), NumberRange(min=5)])
    skills = StringField('技能列表 (用逗号分隔)', validators=[DataRequired(), Length(max=200)])
    certifications = TextAreaField('资质/证书', validators=[Optional()])
    phone = StringField('电话号码', validators=[DataRequired(), Length(max=20)])
    location = StringField('所在地区', validators=[DataRequired(), Length(max=64)])
    
    terms_agree = BooleanField('我同意服务条款和隐私政策', validators=[DataRequired()])
    submit = SubmitField('注册成为专业人士')

    def validate_username(self, username):
        """验证用户名是否已存在"""
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用，请选择其他用户名')

    def validate_email(self, email):
        """验证邮箱是否已存在"""
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册，请使用其他邮箱') 