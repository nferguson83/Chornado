from flask import redirect, render_template, request, url_for, Blueprint, flash
from flask_login import login_required, login_user, logout_user, LoginManager
from werkzeug.security import check_password_hash

from .forms import (LoginForm, ParentRegForm)
from .sql_models import (Parent, Child)
from .helpers import (register_parent, db_commit, flash_errors)

login_manager = LoginManager()
auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(username):
    '''Loads current user into session'''

    user =  Parent.query.filter_by(username=username).first()
    if user is not None and user.type == 'parent':
        return user
    user = Child.query.filter_by(username=username).first()
    return user

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""

    form = LoginForm()

    if request.method == 'POST':
        password = form.password.data
        username = form.username.data
        user = Parent.query.filter_by(username=username).first()
        if user is None:
            user = Child.query.filter_by(username=username).first()

        if user is not None and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('routes.index'))

        flash('Please enter correct username and password', 'error')
        return redirect(url_for('auth.login'))

    flash_errors(form)
    return render_template('login.html', template_form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    '''Logs out current user'''

    logout_user()
    return redirect(url_for('routes.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new parent user"""

    form = ParentRegForm()

    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        register_parent(username, password, first_name, last_name)
        db_commit()
        flash('Account created. Please login.', 'success')
        return redirect(url_for('auth.login'))

    flash_errors(form)
    return render_template('register.html', template_form=form)

@login_manager.unauthorized_handler
def unauthorized():
    '''Handles unauthorized access to pages'''

    return redirect(url_for('routes.index'))
