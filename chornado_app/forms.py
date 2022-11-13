from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, IntegerField, SelectField, HiddenField
from wtforms.validators import DataRequired, EqualTo, Length, ValidationError, NumberRange
from .sql_models import User

# Login form
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Please enter your username")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password")])
    submit = SubmitField('Login')

# Form used for registering primary parent users and child users from parent accounts
class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired("Please enter a username"),
    Length(min=6, max=64, message="Username must be at least 6 characters long")])
    def validate_username(form, field):
        user = User.query.filter_by(username=field.data).first()
        if user is not None:
            print("Username already exists")
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

# Form for creating, editing, and deleting tasks
class ChoreForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired("Please enter a name for the chore")])
    value = IntegerField('Points', validators=[DataRequired("Please enter a point value"),
    NumberRange(min=1, max=9999)])
    child = SelectField('Child', coerce=int)
    chore_id = HiddenField('Chore ID')
    create = SubmitField('Create')
    edit = SubmitField('Edit')
    delete = SubmitField('Delete')
    assign = SubmitField('Assign')

    def __init__(self):
        super(ChoreForm, self).__init__()
        self.child.choices = [(child.id, child.first_name) for child in
        User.query.filter_by(parent=current_user.id).order_by(User.first_name)]

class AssignedChoreForm(FlaskForm):
    chore_id = HiddenField('Chore ID')
    delete = SubmitField('Delete')
    complete = SubmitField('Complete')
    reject = SubmitField('Reject')

class DeleteUserForm(FlaskForm):
    user_id = HiddenField('User ID')
    delete = SubmitField('Delete')
    cancel = SubmitField('Cancel')

class ResetPasswordForm(FlaskForm):
    old_password = PasswordField('Old Password', validators=[DataRequired("Please enter the old password")])
    new_password = PasswordField('New Password', validators=[DataRequired("Please enter a password"),
    Length(min=8, max=64, message="Password length must be at least 8 characters"),
    EqualTo("confirm_password", "Passwords must match")])
    confirm_password = PasswordField('Confirm Password',
    validators=[DataRequired("Please confirm the password")])
    submit = SubmitField('Reset Password')
