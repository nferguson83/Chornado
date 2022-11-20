from flask_login import UserMixin
from . import db

# User table
class User(db.Model, UserMixin):
    """SQLAlchemy User model"""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Establishes whether account is for a parent or child user
    type =  db.Column(db.String(20), nullable=False) 
   
    # For child users only
    points = db.Column(db.Integer) 
    
    # For child users only. Relates to Users.id of parent account    
    parent = db.Column(db.Integer)

    # backref to chores table
    chores = db.relationship('Chore', backref='user', lazy='dynamic',
    cascade='all, delete, delete-orphan')

    # backref to assigned chores table
    assigned_chores = db.relationship('AssignedChore', backref='user',
    lazy='dynamic',cascade='all, delete, delete-orphan')

    # backref to rewards table
    rewards = db.relationship('Reward', backref='user', lazy='dynamic',
    cascade='all, delete, delete-orphan') 

    def __repr__(self):
        return "{}".format(self.username)

class Chore(db.Model):
    """SQLAlchemy model for created chores"""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    
    # Point value of task  
    value = db.Column(db.Integer, nullable=False) 
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    assigned_chores = db.relationship('AssignedChore', backref='chore',
    lazy='dynamic', cascade='all, delete, delete-orphan')
    
    def __repr__(self):
        return "{}".format(self.name)

class AssignedChore(db.Model):
    """SQLAlchemy model for assigned chores"""

    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(24), nullable=False)
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class Reward(db.Model):
    """SQLAlchemy model for created rewards"""

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    cost = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return "{}".format(self.name)

class Notification(db.Model):
    """SQLAlchemy model for active notifications"""

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(12), nullable=False)
    message = db.Column(db.String(256), nullable=False)
    # Change to user ID
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    child_id = db.Column(db.Integer, nullable=False)
    # reward_id
    # chore_id

    def __repr__(self):
        return "{}".format(self.message)