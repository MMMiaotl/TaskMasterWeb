from flask import Blueprint, render_template, request, session, redirect, url_for
from app.models import Task

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    search_query = request.args.get('q', '')
    if search_query:
        tasks = Task.query.filter(Task.title.contains(search_query) | 
                                Task.description.contains(search_query)).all()
    else:
        tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@main_bp.route('/set_language/<language>')
def set_language(language):
    if language in current_app.config['BABEL_SUPPORTED_LOCALES']:
        session['language'] = language
    return redirect(request.referrer or url_for('main.index')) 