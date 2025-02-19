from flask import Blueprint, render_template, flash, redirect, url_for
from flask_login import current_user, login_required
from app.models import User, Review

user_bp = Blueprint('user', __name__)

@user_bp.route('/profile')
@login_required
def user_profile():
    return render_template('user_profile.html', user_info=current_user)

@user_bp.route('/user/<username>')
def other_user_profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user_profile.html', user_info=user)

@user_bp.route('/user/<username>/reviews')
def user_reviews(username):
    user = User.query.filter_by(username=username).first_or_404()
    poster_reviews = Review.query.filter_by(reviewee_id=user.id, role='poster').all()
    executor_reviews = Review.query.filter_by(reviewee_id=user.id, role='executor').all()
    return render_template('user_reviews.html', 
                         user=user, 
                         poster_reviews=poster_reviews,
                         executor_reviews=executor_reviews) 