from flask_wtf import FlaskForm # type: ignore
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, IntegerField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, NumberRange
from app.models import User

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
    title = StringField('标题', validators=[DataRequired(), Length(min=1, max=140)])
    description = TextAreaField('描述', validators=[DataRequired(), Length(min=1, max=1000)])
    submit = SubmitField('提交')

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