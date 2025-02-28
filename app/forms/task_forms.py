from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateField, DecimalField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange
from app.utils.constants import SERVICE_CHOICES

class TaskForm(FlaskForm):
    """任务创建和编辑表单"""
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
    
    deadline = DateField('截止日期', 
        format='%Y-%m-%d',
        validators=[DataRequired(message='请选择截止日期')]
    )
    
    budget = DecimalField('预算 (欧元)', 
        validators=[
            DataRequired(message='请输入任务预算'),
            NumberRange(min=1, message='预算必须大于0')
        ]
    )
    
    submit = SubmitField('发布任务') 