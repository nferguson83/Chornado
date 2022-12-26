from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Parent(db.Model, UserMixin):
    """SQLAlchemy Parent model"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    # Establishes that account is a parent user
    type = db.Column(db.String(8), nullable=False, default='parent')
    # backref to child table
    children = db.relationship('Child', backref='parent', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    # backref to chores table
    chores = db.relationship('Chore', backref='parent', lazy='dynamic',
        cascade='all, delete, delete-orphan')

    # backref to rewards table
    rewards = db.relationship('Reward', backref='parent', lazy='dynamic',
        cascade='all, delete, delete-orphan')

    # backref to notifications table
    notifications = db.relationship('ParentNotification', backref='parent',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"{self.username}"

    def get_id(self):
        return str(self.username)

class Child(db.Model, UserMixin):
    """SQLAlchemy Child model"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    type = db.Column(db.String(8), nullable=False, default='child')
    points = db.Column(db.Integer(), nullable=False, default=0)
    # backref to parents table
    parent_id = db.Column(db.Integer(), db.ForeignKey('parent.id'), nullable=False)
    # backref to assigned chores table
    assigned_chores = db.relationship('AssignedChore', backref='child',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    # backref to notifications table
    notifications = db.relationship('ChildNotification', backref='child',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"{self.username}"

    def get_id(self):
        return str(self.username)

class Chore(db.Model):
    """SQLAlchemy model for created chores"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    # Point value of task
    value = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    # backref to Assigned_Chore table
    assigned_chores = db.relationship('AssignedChore', backref='chore',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return f"{self.name}"

class AssignedChore(db.Model):
    """SQLAlchemy model for assigned chores"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    # Possible states: Active, Complete, Rejected
    state = db.Column(db.String(24), nullable=False)
    # Chore that has been assigned
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    # Child user that chore is assigned to
    user_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    # backref to Notifications table
    parent_notifications = db.relationship('ParentNotification',
        backref='assigned_chore', lazy='dynamic',
        cascade='all, delete, delete-orphan')
    child_notifications = db.relationship('ChildNotification',
        backref='assigned_chore', lazy='dynamic',
        cascade='all, delete, delete-orphan')

class Reward(db.Model):
    """SQLAlchemy model for created rewards"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    cost = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    # backref to Notifications table
    parent_notifications = db.relationship('ParentNotification', backref='reward',
        lazy='dynamic', cascade='all, delete, delete-orphan')
    child_notifications = db.relationship('ChildNotification', backref='reward',
        lazy='dynamic', cascade='all, delete, delete-orphan')

    def __repr__(self):
        return "{self.name}"

class ParentNotification(db.Model):
    """SQLAlchemy model for active parent notifications"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    # Possible types: chore, reward
    type = db.Column(db.String(12), nullable=False)
    # Message string for notification. Will include vars for Chore or Reward
    message = db.Column(db.String(256), nullable=False)
    # ID of parent user owning notification
    parent_id = db.Column(db.Integer, db.ForeignKey('parent.id'), nullable=False)
    # ID of child user that notification references
    child_id = db.Column(db.Integer, nullable=False)
    # References reward that notification relates to
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    # References chore that notification relates to
    chore_id = db.Column(db.Integer, db.ForeignKey('assigned_chore.id'), nullable=True)

    def __repr__(self):
        return "{self.message}"

class ChildNotification(db.Model):
    """SQLAlchemy model for active child notifications"""

    id = db.Column(db.Integer, db.Identity(start=1), primary_key=True)
    # Possible types: chore, reward
    type = db.Column(db.String(12), nullable=False)
    # Message string for notification. Will include vars for Chore or Reward
    message = db.Column(db.String(256), nullable=False)    
    # ID of child user owning notification
    child_id = db.Column(db.Integer, db.ForeignKey('child.id'), nullable=False)
    # References reward that notification relates to
    reward_id = db.Column(db.Integer, db.ForeignKey('reward.id'), nullable=True)
    # References chore that notification relates to
    chore_id = db.Column(db.Integer, db.ForeignKey('assigned_chore.id'), nullable=True)

    def __repr__(self):
        return "{self.message}"