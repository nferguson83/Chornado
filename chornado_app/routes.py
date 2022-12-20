from flask import redirect, render_template, request, url_for, Blueprint
from flask_login import current_user, login_required, logout_user
from werkzeug.security import generate_password_hash

from .forms import *
from .sql_models import *
from .helpers import *

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
@routes_bp.route('/index')
def index():
    """Renders splash screen or parent/child home pages"""

    if not current_user.is_authenticated:
        return render_template('index.html')
    # If logged in user is type: parent, load parent homepage
    elif current_user.type == 'parent':
        return redirect(url_for('parents.home'))
    # If logged in user is type: child, load child homepage
    else:
        return redirect(url_for('children.home'))

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
    else:
        if user is not None and (user.parent == current_user.id or user_id == current_user.id):
            return render_template('delete_user.html', template_form=form, user=user)
        else:
            return redirect(url_for('routes.index'))

@routes_bp.route('/pass_reset/<int:user_id>', methods=['GET', 'POST'])
@login_required
def pass_reset(user_id):
    """Route for resetting child passwords"""
    
    user = User.query.get(user_id)
    form = ChildResetPasswordForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        password = form.new_password.data
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user.password_hash = hash
        db_commit()
        return redirect(url_for('parents.children'))
    
    else:
        if user is not None and user.parent == current_user.id:
            flash_errors(form)
            return render_template('pass_reset.html', template_form=form, user=user)
        else:
            return redirect(url_for('parents.children'))

# Route for testing database inserts and modifications
@routes_bp.route('/test')
def test():
    # new_notification1 = Notification(type='reward', message='Child has requested reward', user_id=21, child_id = 22, reward_id=21)
    # new_notification2 = Notification(type='chore', message='Child says they have finished chore', user_id=21, child_id=22, chore_id=22)

    # db.session.add(new_notification1)
    # db.session.add(new_notification2)

    # chore = AssignedChore.query.get(23)
    # chore.state = 'Complete'
    # notification1 = Notification.query.get(21)
    # notification2 = Notification.query.get(22)
    # notification1.type = 'reward'
    # notification2.type = 'chore'
    # test_query = AssignedChore.query.get(25)
    # if test_query == True:
    #     print(test_query)
    # else:
    #     print(False)
    # new_chore = AssignedChore(state='Completed', chore_id='23', user_id='22')
    # db.session.add(new_chore)
    # try:
    #     db.session.commit()
    #     print("Commit successful")
    # except:
    #     db.session.rollback()
    #     print("Commit failed")
    return redirect(url_for('routes.index'))
    
    pass