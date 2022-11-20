from flask import request, url_for
from werkzeug.security import generate_password_hash
from sqlalchemy import exc

from . import db
from .forms import *
from .sql_models import *

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
    except exc.SQLAlchemyError:
        db.session.rollback()
        return False

def register_user(username, password, first_name, last_name, type, points=None,
parent=None):
    """Register new parent and child users"""
    hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
    new_user = User(username=username, first_name=first_name, last_name=last_name,
        password_hash=hash, type=type, points=points, parent=parent)
    db.session.add(new_user)

def create_chore(name, value, parent_id):
    """Add new chore to database"""
    new_chore = Chore(name=name, value=value, parent_id=parent_id)
    db.session.add(new_chore)

def assign_chore(chore_id, user_id):
    """Assign chore from database to child"""
    new_assigned_chore = AssignedChore(state='Active', chore_id=chore_id,
    user_id=user_id)
    db.session.add(new_assigned_chore)

def edit_chore(chore, name, value):
    """Edit existing chore"""
    chore.name = name
    chore.value = value
    return chore

def approve_completed(chore, child, new_points):
    """Approve completed chore, and assign points to child"""
    child.points += new_points
    db.session.delete(chore)
    return child
    
def create_reward(name, cost, parent_id):
    """Add new reward to database"""
    new_reward = Reward(name=name, cost=cost, parent_id=parent_id)
    db.session.add(new_reward)

def edit_reward(reward, name, cost):
    """Edit existing reward"""
    reward.name = name
    reward.cost = cost
    return reward