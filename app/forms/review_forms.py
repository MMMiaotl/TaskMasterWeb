from flask_wtf import FlaskForm
from wtforms import IntegerField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange

class ReviewForm(FlaskForm):
    """用户评价表单"""
    rating = IntegerField('评分', validators=[
        DataRequired(),
        NumberRange(min=1, max=5, message='评分必须在1-5之间')
    ])
    content = TextAreaField('评价内容', validators=[
        DataRequired(),
        Length(min=10, max=500)
    ])
    submit = SubmitField('提交评价') 