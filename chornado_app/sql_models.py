from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# User table
class User(db.Model, UserMixin):
    """SQLAlchemy User model"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Establishes whether account is for a parent or child user
    type =  db.Column(db.String(20), nullable=False) # If re-initiating DB, change to user_type or remove if splitting user tables
    # For child users only
    points = db.Column(db.Integer, nullable=True) 
    # For child users only. Relates to Users.id of parent account
    parent = db.Column(db.Integer, nullable=True)
    # backref to chores table
    chores = db.relationship('Chore', backref='user', lazy='dynamic',
        cascade='all, delete, delete-orphan')

    # backref to assigned chores table
    assigned_chores = db.relationship('AssignedChore', backref='user',
        lazy='dynamic',cascade='all, delete, delete-orphan')

    # backref to rewards table
    rewards = db.relationship('Reward', backref='user', lazy='dynamic',
        cascade='all, delete, delete-orphan')

    # backref to notifications table
    notifications = db.relationship('Notification', backref='user',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"{self.username}"

class Chore(db.Model):
    """SQLAlchemy model for created chores"""
    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    # Point value of task
    value = db.Column(db.Integer, nullable=False) 
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # backref to Assigned_Chore table
    assigned_chores = db.relationship('AssignedChore', backref='chore',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "{self.name}"

class AssignedChore(db.Model):
    """SQLAlchemy model for assigned chores"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    # Possible states: Active, Complete, Rejected
    state = db.Column(db.String(24), nullable=False)
    # Chore that has been assigned
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    # Child user that chore is assigned to
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # backref to Notifications table
    notifications = db.relationship('Notification', backref='assigned_chore',
        lazy='dynamic', cascade='all, delete, delete-orphan')

class Reward(db.Model):
    """SQLAlchemy model for created rewards"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    cost = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # backref to Notifications table
    notifications = db.relationship('Notification', backref='reward',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "{self.name}"

class Notification(db.Model):
    """SQLAlchemy model for active notifications"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    # Possible types: chore, reward
    type = db.Column(db.String(12), nullable=False)
    # Message string for notification. Will include vars for Chore or Reward
    message = db.Column(db.String(256), nullable=False)
    # ID of parent user owning notification
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # ID of child user that notification references
    child_id = db.Column(db.Integer, nullable=False)
    # References reward that notification relates to
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    # References chore that notification relates to
    chore_id = db.Column(db.Integer, db.ForeignKey('assigned_chore.id'), nullable=True)

    def __repr__(self):
        return "{self.message}"
