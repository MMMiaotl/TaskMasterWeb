from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

class MessageForm(FlaskForm):
    """消息发送表单"""
    content = TextAreaField('消息内容', validators=[
        DataRequired(), 
        Length(min=1, max=1000)
    ])
    submit = SubmitField('发送') 