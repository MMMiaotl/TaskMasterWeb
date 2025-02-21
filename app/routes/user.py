from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.forms import EditProfileForm
from app.models import User, Review
from werkzeug.utils import secure_filename
import os
from config import Config

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def user_profile():
    return render_template('user_profile.html', user_info=current_user)

@user_bp.route('/profile/<username>')
def other_user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user_info=user)

@user_bp.route('/user/<username>')
def user_reviews(username):
    user = User.query.filter_by(username=username).first_or_404()
    poster_reviews = Review.query.filter_by(reviewee_id=user.id, role='poster').all()
    executor_reviews = Review.query.filter_by(reviewee_id=user.id, role='executor').all()
    return render_template('user_reviews.html', 
                         user=user, 
                         poster_reviews=poster_reviews,
                         executor_reviews=executor_reviews)

@user_bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.phone = form.phone.data
        current_user.bio = form.bio.data
        current_user.location = form.location.data
        current_user.website = form.website.data
        db.session.commit()
        flash('个人资料已更新')
        return redirect(url_for('user.user_profile'))
    elif request.method == 'GET':
        form.phone.data = current_user.phone
        form.bio.data = current_user.bio
        form.location.data = current_user.location
        form.website.data = current_user.website
    return render_template('edit_profile.html', form=form)

@user_bp.route('/user/<username>/edit_avatar', methods=['GET', 'POST'])
@login_required
def edit_avatar(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.id != current_user.id:
        flash('你没有权限编辑此用户的头像。', 'error')
        return redirect(url_for('user.user_profile', username=username))
    
    if request.method == 'POST':
        file = request.files.get('avatar')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
            file.save(filepath)
            user.avatar_url = url_for('static', filename=f'uploads/{filename}')
            db.session.commit()
            flash('头像更新成功！', 'success')
            return redirect(url_for('user.user_profile', username=username))
        else:
            flash('文件类型不支持，请上传图片文件。', 'error')
    
    return render_template('edit_avatar.html', user=user)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'} 