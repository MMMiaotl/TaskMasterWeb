from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField, DateTimeField, DecimalField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User
from app.utils.constants import SERVICE_CHOICES

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired(), Length(min=6)])
    password2 = PasswordField('确认密码', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('该用户名已被使用')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('该邮箱已被注册')

class TaskForm(FlaskForm):
    title = StringField('任务标题', validators=[
        DataRequired(message='请输入任务标题'),
        Length(min=2, max=100, message='标题长度必须在2-100字符之间')
    ])
    
    service_category = SelectField('服务类别', 
        choices=SERVICE_CHOICES,
        validators=[DataRequired(message='请选择服务类别')]
    )
    
    description = TextAreaField('任务描述', validators=[
        DataRequired(message='请输入任务描述'),
        Length(min=10, max=1000, message='描述长度必须在10-1000字符之间')
    ])
    
    location = StringField('地点', validators=[
        DataRequired(message='请输入任务地点'),
        Length(max=100)
    ])
    
    deadline = DateTimeField('截止日期', 
        format='%Y-%m-%dT%H:%M',
        validators=[DataRequired(message='请选择截止日期')]
    )
    
    budget = DecimalField('预算 (元)', 
        validators=[
            DataRequired(message='请输入任务预算'),
            NumberRange(min=1, message='预算必须大于0')
        ]
    )
    
    submit = SubmitField('发布任务')

class ReviewForm(FlaskForm):
    content = TextAreaField('Review Content', validators=[DataRequired()])
    rating = IntegerField('Rating (1-5)', validators=[DataRequired(), NumberRange(min=1, max=5)])
    role = SelectField('Role', choices=[('poster', 'As Poster'), ('executor', 'As Executor')], validators=[DataRequired()])
    submit = SubmitField('Submit Review')

class MessageForm(FlaskForm):
    content = TextAreaField('消息内容', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('发送')

class EditProfileForm(FlaskForm):
    phone = StringField('电话号码')
    bio = TextAreaField('个人简介', validators=[Length(max=500)])
    location = StringField('所在地', validators=[Length(max=64)])
    website = StringField('个人网站', validators=[Length(max=128)])
    submit = SubmitField('保存修改')