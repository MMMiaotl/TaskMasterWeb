from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import Length

class EditProfileForm(FlaskForm):
    """个人资料编辑表单"""
    phone = StringField('电话号码')
    bio = TextAreaField('个人简介', validators=[Length(max=500)])
    location = StringField('所在地', validators=[Length(max=64)])
    website = StringField('个人网站', validators=[Length(max=128)])
    submit = SubmitField('保存修改') 