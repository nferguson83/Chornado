from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import login_required, login_user, logout_user, LoginManager
from werkzeug.security import check_password_hash

from .forms import *
from .sql_models import *
from .helpers import *

login_manager = LoginManager()
auth_bp = Blueprint('auth', __name__)

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""

    form = LoginForm()
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('routes.index'))
        else:
            error = 'Please enter correct username and password' # Change to flash message (categories)
            return render_template('login.html', template_form=form, error=error)
    else:
        return render_template('login.html', template_form=form)

@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.index'))

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Register new parent user"""    
    
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        register_user(username, password, first_name, last_name, "parent")
        success = 'Account created. Please login.' # Change to flash message
        db_commit()
        return render_template('login.html', template_form=form,
        success=success) # Change to redirect?
    else:
        return render_template('register.html', template_form=form)

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('routes.index'))