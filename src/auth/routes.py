from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user
from src.auth.forms import LoginForm, RegisterForm
from src.models import User
from src import db
from . import bp

# bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('app.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.validate_password(form.password.data):
            login_user(user)
            flash('Logged In', category='success')
            return redirect(url_for('app.dashboard'))
        
        flash('Invalid username/password', category='error')
    
    return render_template('auth/login.html', form=form)



@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('app.dashboard'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created', category='success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/register.html', form=form)



@bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('auth.login'))