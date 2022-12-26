from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import (StringField, SubmitField, PasswordField, IntegerField,
    SelectField, HiddenField)
from wtforms.validators import (InputRequired, EqualTo, Length, ValidationError,
    NumberRange, Email)
from .sql_models import (Parent, Child, AssignedChore)

class LoginForm(FlaskForm):
    """Form for logging in users"""

    username = StringField('Username',
        validators=[InputRequired("Please enter your username"), Email()])

    password = PasswordField('Password',
        validators=[InputRequired("Please enter your password")])

    submit = SubmitField('Login')

class ParentRegForm(FlaskForm):
    """Form used for registering primary parent users"""

    username = StringField('Email Address',
        validators=[InputRequired("Please enter a username"),
        Length(min=8, max=64, message="Username must be at least 8 characters long"),
        Email("Username must be an email address")])

    def validate_username(self, field):
        '''Custom validator to check that username is unique'''

        parent_user = Parent.query.filter_by(username=field.data).first()
        child_user = Child.query.filter_by(username=field.data).first()
        if parent_user is not None or child_user is not None:
            raise ValidationError("Username already exists")
        

    first_name = StringField('First name',
        validators=[InputRequired("Please enter your first name"),
        Length(min=2, max=64, message="First name must be at least 2 letters long")])

    last_name = StringField('Last name',
        validators=[InputRequired("Please enter your last name"),
        Length(min=2, max=64, message="Last name must be at least 2 letters long")])

    password = PasswordField('Password',
        validators=[InputRequired("Please enter a password"),
        Length(min=8, max=64, message="Password length must be at least 8 characters long"),
        EqualTo("confirm_password", "Passwords must match")])

    confirm_password = PasswordField('Confirm Password',
        validators=[InputRequired("Please confirm the password")])

    submit = SubmitField('Register')

class ChildRegForm(FlaskForm):
    """Form used for registering child users"""

    username = StringField('Username', validators=[InputRequired("Please enter a username"),
        Length(min=6, max=64, message="Username must be at least 6 characters long")])

    def validate_username(self, field):
        '''Custom validator to check that username is unique'''

        parent_user = Parent.query.filter_by(username=field.data).first()
        child_user = Child.query.filter_by(username=field.data).first()
        if parent_user is not None or child_user is not None:
            raise ValidationError("Username already exists")

    first_name = StringField('First name',
        validators=[InputRequired("Please enter your first name"),
        Length(min=2, max=64, message="First name must be at least 2 letters long")])

    password = PasswordField('Password',
        validators=[InputRequired("Please enter a password"),
        Length(min=8, max=64, message="Password length must be at least 8 characters long"),
        EqualTo("confirm_password", "Passwords must match")])

    confirm_password = PasswordField('Confirm Password',
        validators=[InputRequired("Please confirm the password")])

    submit = SubmitField('Register')

class ChoreForm(FlaskForm):
    """Form for creating, editing, and deleting tasks"""

    name = StringField('Name',
        validators=[InputRequired("Please enter a name for the chore")])

    value = IntegerField('Points',
        validators=[InputRequired("Please enter a point value"),
        NumberRange(min=1, max=9999)])

    child = SelectField('Child', coerce=int)
    chore_id = HiddenField('Chore ID')
    create = SubmitField('Create')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    assign = SubmitField('Assign')

    # Method for capturing child accounts for SelectField
    def __init__(self):
        super().__init__()
        self.child.choices = [(child.id, child.first_name) for child in
        current_user.children.order_by(Child.first_name)]

    def validate_assign(form, field):
        '''Validates that chore isn't already assigned to child'''

        if form.assign.data:
            chore = AssignedChore.query.filter_by(user_id=form.child.data,
            chore_id=form.chore_id.data).first()
            if chore is not None:
                raise ValidationError("This chore has already been assigned to this child.")

class AssignedChoreForm(FlaskForm):
    """Form for approving, rejecting, completing and deleting assigned chores"""

    chore_id = HiddenField('Chore ID')
    delete = SubmitField('Delete')
    approve = SubmitField('Approve')
    reject = SubmitField('Reject')
    complete = SubmitField('Complete')


class DeleteUserForm(FlaskForm):
    """Form for deleting users"""

    user_id = HiddenField('User ID')
    delete = SubmitField('Delete')

class ParentResetPasswordForm(FlaskForm):
    """Form for resetting parent passwords"""

    old_password = PasswordField('Old Password',
        validators=[InputRequired("Please enter the old password")])

    new_password = PasswordField('New Password',
        validators=[InputRequired("Please enter a password"),
        Length(min=8, max=64, message="Password length must be at least 8 characters"),
        EqualTo("confirm_password", "New passwords must match")])

    confirm_password = PasswordField('Confirm Password',
        validators=[InputRequired("Please confirm the password")])

    submit = SubmitField('Reset Password')

class ChildResetPasswordForm(FlaskForm):
    """Form for resetting child passwords"""

    user_id = HiddenField('User ID')
    new_password = PasswordField('New Password',
        validators=[InputRequired("Please enter a password"),
        Length(min=8, max=64, message="Password length must be at least 8 characters"),
        EqualTo("confirm_password", "Passwords must match")])

    confirm_password = PasswordField('Confirm Password',
        validators=[InputRequired("Please confirm the password")])

    submit = SubmitField('Reset Password')

class RewardForm(FlaskForm):
    """Form for adding, editing, and deleting rewards"""

    name = StringField('Name',
        validators=[InputRequired("Please enter a name for the reward")])

    cost = IntegerField('Points',
        validators=[InputRequired("Please enter a point cost for the reward"),
        NumberRange(min=1, max=9999)])

    reward_id = HiddenField('Reward ID')
    notification_id = HiddenField('Notification ID')
    create = SubmitField('Create')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    deliver = SubmitField('Deliver')
    purchase = SubmitField('Purchase')

class NotificationForm(FlaskForm):
    """Form for acknowledging notifications for children"""

    notification_id = HiddenField('Notification ID')
    acknowledge = SubmitField('Accept')

class PointsForm(FlaskForm):
    """Form for adding and removing points from children"""

    child_id = HiddenField('Child ID')
    points = IntegerField('Points', validators=[NumberRange(min=-9999, max=9999)])
    adjust = SubmitField('Adjust')
