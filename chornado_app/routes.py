from flask import redirect, render_template, request, url_for, Blueprint, flash
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from .forms import (DeleteUserForm, ChildResetPasswordForm, LoginForm)
from .sql_models import (db, Parent, Child, ParentNotification)
from .helpers import (db_commit, flash_errors, redirect_url)

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
@routes_bp.route('/index')
def index():
    """Renders splash screen or parent/child home pages"""

    if not current_user.is_authenticated:
        form = LoginForm()
        return render_template('index.html', template_form=form)
    # If logged in user is type: parent, load parent homepage
    if current_user.type == 'parent':
        return redirect(url_for('parent.home'))

    # If logged in user is type: child, load child homepage
    return redirect(url_for('child.home'))

@routes_bp.route('/delete_child/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_child(user_id):
    """Route for deleting child users"""

    user = Child.query.get(user_id)
    form = DeleteUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        # Identify notifications linked to child account for deletion
        notifications = ParentNotification.query.filter_by(child_id=user.id).all()
        for notification in notifications:
            db.session.delete(notification)
        flash(f'{user.first_name} has been deleted.', 'success')
        db.session.delete(user)
        db_commit()
        return redirect(url_for('parent.children'))

    if user is not None and user in current_user.children:
        return render_template('delete_child.html', template_form=form,
            user=user)
    
    return redirect(url_for('routes.index'))
        
@routes_bp.route('/delete_parent/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_parent(user_id):
    """Route for deleting parent users"""

    user = Parent.query.get(user_id)
    form = DeleteUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        flash(f'{user.first_name} has been deleted.', 'success')
        logout_user()
        db.session.delete(user)
        db_commit()
        return redirect(url_for('routes.index'))

    if user is not None and user == current_user:
        return render_template('delete_parent.html', template_form=form,
            user=user)

    return redirect(url_for('routes.index'))

@routes_bp.route('/pass_reset/<int:user_id>', methods=['GET', 'POST'])
@login_required
def pass_reset(user_id):
    """Route for resetting child passwords"""

    user = Child.query.get(user_id)
    form = ChildResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        password = form.new_password.data
        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user.password_hash = pw_hash
        db_commit()
        return redirect(url_for('parent.children'))

    if user is not None and user.parent_id == current_user.id:
        flash_errors(form)
        return render_template('pass_reset.html', template_form=form, user=user)

    return redirect(url_for('parent.children'))
