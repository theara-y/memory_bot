from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

bp = Blueprint('app', __name__)

@bp.before_request
def check_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))

@bp.route('/')
def index():
    return redirect(url_for('app.dashboard'))

@bp.route('/dashboard')
def dashboard():
    return render_template('app/dashboard.html')