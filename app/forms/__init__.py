from app.forms.auth_forms import LoginForm, RegistrationForm
from app.forms.task_forms import TaskForm
from app.forms.review_forms import ReviewForm
from app.forms.message_forms import MessageForm
from app.forms.profile_forms import EditProfileForm

# 导出所有表单类，保持向后兼容性
__all__ = [
    'LoginForm', 
    'RegistrationForm', 
    'TaskForm', 
    'ReviewForm', 
    'MessageForm', 
    'EditProfileForm'
] 