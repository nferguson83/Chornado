from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, NumberRange
from .sql_models import User, AssignedChore

class LoginForm(FlaskForm):
    """Form for logging in users"""
    
    username = StringField('Username', validators=[DataRequired("Please enter your username")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password")])
    submit = SubmitField('Login')

class RegisterForm(FlaskForm):
    """Form used for registering primary parent users and child
    users from parent accounts"""

    username = StringField('Username', validators=[DataRequired("Please enter a username"),
    Length(min=6, max=64, message="Username must be at least 6 characters long")])
    
    # Validates that user doesn't already exist    
    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:        
            raise ValidationError("Username already exists")
    
    first_name = StringField('First name', validators=[DataRequired("Please enter your first name"),
    Length(min=2, max=64, message="First name must be at least 2 letters long")])
    
    last_name = StringField('Last name', validators=[DataRequired("Please enter your last name"),
    Length(min=2, max=64, message="Last name must be at least 2 letters long")])
        
    password = PasswordField('Password', validators=[DataRequired("Please enter a password"),
    Length(min=8, max=64, message="Password length must be at least 8 characters long"),
    EqualTo("confirm_password", "Passwords must match")])
    
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired("Please confirm the password")])
    
    submit = SubmitField('Register')

class ChoreForm(FlaskForm):
    """Form for creating, editing, and deleting tasks"""
    
    name = StringField('Name', validators=[DataRequired("Please enter a name for the chore")])
    value = IntegerField('Points', validators=[DataRequired("Please enter a point value"),
    NumberRange(min=1, max=9999)])
    
    child = SelectField('Child', coerce=int)
    chore_id = HiddenField('Chore ID')
    create = SubmitField('Create')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    assign = SubmitField('Assign')

    # Method for capturing child accounts for SelectField
    def __init__(self):
        super(ChoreForm, self).__init__()
        self.child.choices = [(child.id, child.first_name) for child in
        User.query.filter_by(parent=current_user.id).order_by(User.first_name)]

    # Validate that chore isn't already assigned to child
    def validate_assign(form, field):
        if form.assign.data:
            chore = AssignedChore.query.filter_by(user_id=form.child.data,
            chore_id=form.chore_id.data).first()
            if chore is not None:
                raise ValidationError("This chore has already been assigned to this child.")

class AssignedChoreForm(FlaskForm):
    """Form for approving, rejecting, and deleting completed chores"""
    
    chore_id = HiddenField('Chore ID')
    delete = SubmitField('Delete')
    approve = SubmitField('Approve')
    reject = SubmitField('Reject')

class DeleteUserForm(FlaskForm):
    """Form for deleting users"""

    user_id = HiddenField('User ID')
    delete = SubmitField('Delete')

class ParentResetPasswordForm(FlaskForm):
    """Form for resetting parent passwords"""

    user_id = HiddenField('User ID')
    old_password = PasswordField('Old Password',
    validators=[DataRequired("Please enter the old password")])
        
    new_password = PasswordField('New Password',
    validators=[DataRequired("Please enter a password"),
    Length(min=8, max=64, message="Password length must be at least 8 characters"),
    EqualTo("confirm_password", "Passwords must match")])
    
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired("Please confirm the password")])
    
    submit = SubmitField('Reset Password')

class ChildResetPasswordForm(FlaskForm):
    """Form for resetting child passwords"""

    user_id = HiddenField('User ID')
    new_password = PasswordField('New Password',
    validators=[DataRequired("Please enter a password"),
    Length(min=8, max=64, message="Password length must be at least 8 characters"),
    EqualTo("confirm_password", "Passwords must match")])
    
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired("Please confirm the password")])
    
    submit = SubmitField('Reset Password')

class RewardForm(FlaskForm):
    """Form for adding, editing, and deleting rewards"""

    name = StringField('Name',
    validators=[DataRequired("Please enter a name for the chore")])
    
    cost = IntegerField('Points', validators=[DataRequired("Please enter a point value"),
    NumberRange(min=1, max=9999)])
    
    reward_id = HiddenField('Reward ID')
    create = SubmitField('Create')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    deliver = SubmitField('Deliver')
    purchase = SubmitField('Purchase')