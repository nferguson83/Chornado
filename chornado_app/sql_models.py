from app import app, db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    first_name = db.Column(db.String(64), nullable=False)
    last_name = db.Column(db.String(64), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    type =  db.Column(db.String(20), nullable=False) # Establishes whether account is for a parent or child user
    points = db.Column(db.Integer) # For child users only
    parent = db.Column(db.Integer) # For child users only. Relates to Users.id of parent account
    chores = db.relationship('Chore', backref='user', lazy='dynamic') # backref to chores table
    assigned_chores = db.relationship('AssignedChore', backref='user', lazy='dynamic') # backref to assigned chores table

    def __repr__(self):
        return "{}".format(self.username)

class Chore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(256), nullable=False, index=True)
    value = db.Column(db.Integer, nullable=False) # Point value of task
    parent_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False) 
    assigned_chores = db.relationship('AssignedChore', backref='chore', lazy='dynamic')
    
    def __repr__(self):
        return "{}".format(self.name)

class AssignedChore(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(24), nullable=False)
    chore_id = db.Column(db.Integer, db.ForeignKey('chore.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)