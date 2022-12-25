from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from .forms import (DeleteUserForm, ChildResetPasswordForm)
from .sql_models import (db, User, Notification)
from .helpers import (db_commit, flash_errors)

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
@routes_bp.route('/index')
def index():
    """Renders splash screen or parent/child home pages"""

    if not current_user.is_authenticated:
        return render_template('index.html')
    # If logged in user is type: parent, load parent homepage
    if current_user.type == 'parent':
        return redirect(url_for('parent.home'))
    # If logged in user is type: child, load child homepage

    return redirect(url_for('child.home'))

@routes_bp.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    """Route for deleting users"""

    user = User.query.get(user_id)
    form = DeleteUserForm()

    if request.method == 'POST' and form.validate_on_submit():
        if user.type == 'parent':
            # Identify child accounts linked to parent account for deletion
            children = User.query.filter_by(parent=user.id).all()
            for child in children:
                db.session.delete(child)
            logout_user()
            db.session.delete(user)
        else:
            # Identify notifications linked to child account for deletion
            notifications = Notification.query.filter_by(child_id=user.id).all()
            for notification in notifications:
                db.session.delete(notification)
            db.session.delete(user)

        db_commit()
        return redirect(url_for('routes.index'))

    if user is not None and (current_user.id in (user.parent, user_id)):
        return render_template('delete_user.html', template_form=form,
            user=user)

    return redirect(url_for('routes.index'))

@routes_bp.route('/pass_reset/<int:user_id>', methods=['GET', 'POST'])
@login_required
def pass_reset(user_id):
    """Route for resetting child passwords"""

    user = User.query.get(user_id)
    form = ChildResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        password = form.new_password.data
        pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user.password_hash = pw_hash
        db_commit()
        return redirect(url_for('parent.children'))

    if user is not None and user.parent == current_user.id:
        flash_errors(form)
        return render_template('pass_reset.html', template_form=form, user=user)

    return redirect(url_for('parent.children'))

# Route for testing database inserts and modifications
@routes_bp.route('/test')
def test():
#     notifications = current_user.notifications
#     for notification in notifications:
#         db.session.delete(notification)
#     db_commit()
    return redirect(url_for('routes.index'))
