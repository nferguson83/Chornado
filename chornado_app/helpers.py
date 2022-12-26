from flask import request, url_for, flash
from flask_login import current_user
from werkzeug.security import generate_password_hash
from sqlalchemy import exc

from .sql_models import (db, Chore, AssignedChore, Parent, Child, Reward,
    ParentNotification, ChildNotification)

def redirect_url(default='home'):
    """Redirect back to referring page"""
    return request.args.get('next') or \
           request.referrer or \
           url_for(default)

def db_commit():
    """Attempt to commit changes to database.
        Returns true if successful"""

    try:
        db.session.commit()
        return True
    except exc.SQLAlchemyError as error:
        print(error)
        db.session.rollback()
        return False

def register_parent(username, password, first_name, last_name):
    """Register new parent users
    Args: (username, password, first_name, last_name)"""

    pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    new_user = Parent(username=username, first_name=first_name, last_name=last_name,
        password_hash=pw_hash)
    db.session.add(new_user)

def register_child(username, password, first_name):
    """Register new parent and child users
    Args: (username, password, first_name)"""

    pw_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    new_user = Child(username=username, first_name=first_name, password_hash=pw_hash,
        parent=current_user)
    db.session.add(new_user)

def create_chore(name, value, parent_id):
    """Add new chore to database
    Args: (name, value, parent_id)"""

    new_chore = Chore(name=name, value=value, parent_id=parent_id)
    db.session.add(new_chore)

def assign_chore(chore_id, user_id):
    """Assign chore from database to child
    Args: (chore_id, user_id)"""

    new_assigned_chore = AssignedChore(state='Active', chore_id=chore_id,
        user_id=user_id)
    db.session.add(new_assigned_chore)

def edit_chore(chore, name, value):
    """Edit existing chore
    Args: (chore, name, value)"""

    chore.name = name
    chore.value = value
    return chore

def complete_chore(chore_id):
    """Mark chore as completed and generate notification to parent
    Args: (chore_id)"""

    assigned_chore = AssignedChore.query.get(chore_id)
    child = Child.query.get(assigned_chore.user_id)
    chore = Chore.query.get(assigned_chore.chore_id)
    assigned_chore.state = 'Complete'
    message = f'{child.first_name} has completed {chore.name}.'
    new_notification = ParentNotification(type='chore', message=message,
        parent_id=child.parent_id, child_id=child.id, chore_id=chore_id)   

    db.session.add(new_notification)
    db_commit()

def approve_completed(chore, child, new_points):
    """Approve completed chore, and assign points to child
    Args: (chore, child, new_points)"""

    child.points += new_points
    db.session.delete(chore)
    return child

def reject_completed(chore):
    """Reject completed chore, and remove attached notifications
    Args: (chore)"""

    chore.state = 'Rejected'
    notifications = chore.parent_notifications
    for notification in notifications:
        db.session.delete(notification)
    chore_name = Chore.query.get(chore.chore.id).name
    child_id = chore.user_id
    message = f'Your parent says that {chore_name} needs another try.'
    new_notification = ChildNotification(type='chore', message=message,
        child_id=child_id, chore_id=chore.id)
    db.session.add(new_notification)
    db_commit()
    return chore

def create_reward(name, cost, parent_id):
    """Add new reward to database
    Args: (name, cost, parent_id)"""

    new_reward = Reward(name=name, cost=cost, parent_id=parent_id)
    db.session.add(new_reward)

def edit_reward(reward, name, cost):
    """Edit existing reward
    Args: (reward, name, cost)"""

    reward.name = name
    reward.cost = cost
    return reward

def request_reward(user, reward):
    """Request reward from list, deduct points, and send notification to parent
    Args: (user, reward)"""

    user.points -= reward.cost
    message = f'{user.first_name} has purchased {reward.name}'
    new_notification = ParentNotification(type='reward', message=message,
        parent_id=user.parent_id, child_id=user.id, reward_id=reward.id)
    db.session.add(new_notification)
    db_commit()
    return user

def flash_errors(form):
    """Flash form errors to template.
    Function inspired by Sean W. on StackOverflow.
    Args: (form)"""

    for field, errors in form.errors.items():
        for error in errors:
            flash(error, 'error')
