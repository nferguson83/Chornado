from flask import redirect, render_template, request, url_for, flash
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from sqlalchemy import exc

from . import app, db, login_manager
from .forms import *
from .sql_models import *
from .helpers import *

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/')
@app.route('/index')
def index():
    """Renders splash screen or parent/child home pages"""

    if not current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('home'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""

    form = LoginForm()
    if request.method == 'POST':
        password = request.form['password']
        username = request.form['username']
        user = User.query.filter_by(username=username).first()
        if user is not None and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = 'Please enter correct username and password'
            return render_template('login.html', template_form=form, error=error)
    else:
        return render_template('login.html', template_form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register new parent user"""    
    
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        register_user(username, password, first_name, last_name, "parent")
        success = 'Account created. Please login.'
        db_commit()
        return render_template('login.html', template_form=form,
        success=success)
    else:
        return render_template('register.html', template_form=form)
            
@app.route('/home')
@login_required
def home():
    """Homepages for parents and children"""
    
    # If logged in user is type: parent, load parent homepage
    if current_user.type == 'parent':
        parent = current_user.id
        children = User.query.filter_by(parent=parent).order_by(User.first_name)
        child_data = []
        notifications = Notification.query.filter_by(parent_id=parent).order_by(Notification.message)
        chore_form = AssignedChoreForm()
        reward_form = RewardForm()
        
        # Create list of dictionaries of data for children
        # and count of the chores assigned to them
        for child in children:
            chores = AssignedChore.query.filter_by(user_id=child.id).count()
            child_dict = {'username': child.username, 'first_name': child.first_name,
            'points': child.points, 'chores': chores}
            child_data.append(child_dict)
        return render_template('parent_home.html', child_data=child_data,
        notifications=notifications, chore_form=chore_form, reward_form=reward_form)
    
    # If logged in user is type: child, load child homepage
    else:
        return render_template('child_home.html')

@app.route('/children', methods=['GET', 'POST'])
@login_required
def children():
    """Parent's children page for listing and creating child accounts"""
    
    register_form = RegisterForm()
    chore_form = AssignedChoreForm()
    parent = current_user.id    
    
    if request.method == 'POST' and register_form.validate_on_submit():
        # Register new child account
        if register_form.submit.data:
            username = register_form.username.data
            password = register_form.password.data
            first_name = register_form.first_name.data
            last_name = register_form.last_name.data
            register_user(username, password, first_name, last_name, "child",
            0, parent)
            flash(f'Account created for {first_name}')

    elif request.method == 'POST' and chore_form.validate_on_submit():    
        current_chore = AssignedChore.query.get(chore_form.chore_id.data)
        
        # Approve completed chore, assign points, and delete assigned chore
        if chore_form.approve.data:            
            new_points = Chore.query.get(current_chore.chore_id).value
            child = User.query.get(current_chore.user_id)
            approve_completed(current_chore, child, new_points)
            flash(f'{current_chore.name} complete!')
        
        # Delete assigned chore
        elif chore_form.delete.data:
            db.session.delete(current_chore)
            flash(f'{current_chore.name} has been removed for {child.first_name}')
        
        # Reject completed chore, and set status back to active
        elif chore_form.reject.data:
            current_chore.state = 'Active'
            flash(f'{current_chore.name} has been sent back to {child.first_name}')
        db_commit()
        return redirect(redirect_url())
    
    else:
        children = User.query.filter_by(parent=parent).order_by(User.first_name)
        child_data = []
        
        # Create list of dictionaries of data for children
        # and the chores assigned to them
        for child in children:
            chores = []
            assigned_chores = AssignedChore.query.filter_by(user_id=child.id).order_by(AssignedChore.id)
            for assigned_chore in assigned_chores:
                chore_info = Chore.query.get(assigned_chore.chore_id)
                chore_dict = {'id': assigned_chore.id, 'name': chore_info.name,
                'points': chore_info.value, 'state': assigned_chore.state}
                
                chores.append(chore_dict)
            
            child_dict = {'username': child.username, 'first_name': child.first_name,
            'points': child.points, 'id': child.id, 'chores': chores}

            child_data.append(child_dict)

        return render_template('children.html', template_form=register_form,
        chore_form=chore_form, child_data=child_data)

@app.route('/parent_chores', methods=['GET', 'POST'])
@login_required
def parent_chores():
    """Parent's chore page for creating, viewing, editing, and assigning chores"""
    
    parent = current_user.id
    form = ChoreForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        value = form.value.data
        child = User.query.get(form.child.data)
        chore_id = form.chore_id.data
        chore = Chore.query.get(chore_id)
        
        # Create new chore
        if form.create.data:
            create_chore(name, value, parent)
        
        # Assign chore to child
        elif form.assign.data:
            assign_chore(chore_id, child.id)
            flash(f'{chore.name} assigned to {child.first_name}')
        
        # Edit existing chore
        elif form.edit.data:
            edit_chore(chore, name, value)            
            flash(f'{chore.name} has been updated')
        
        # Delete chore        
        elif form.delete.data:
            db.session.delete(chore)
        db_commit()
        return redirect(redirect_url())
    
    else:
        chores = Chore.query.filter_by(parent_id=parent).order_by(Chore.name)
        return render_template('parent_chores.html', template_form=form, chores=chores)

@app.route('/parent_rewards', methods=['GET', 'POST'])
@login_required
def parent_rewards():
    """Route for viewing, creating, and editing rewards"""
    # Need to abstract functions out

    form = RewardForm()
    parent = current_user.id
        
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        reward_id = form.reward_id.data
        reward = Reward.query.get(reward_id)
        if form.create.data:
            create_reward(name, cost, parent)
        elif form.edit.data:
            edit_reward(reward, name, cost)
        elif form.delete.data:
            db.session.delete(reward)
        db_commit()
        return redirect(redirect_url())
    else:
        rewards = Reward.query.filter_by(parent_id=parent).order_by(Reward.name)
        return render_template('parent_rewards.html', template_form=form,
        rewards=rewards)


@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
@login_required
def delete_user(user_id):
    """Route for deleting users"""
    form = DeleteUserForm()
    user = User.query.get(user_id)
    
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
        return redirect(url_for('home'))
    
    else:
        if user is not None and (user.parent == current_user.id or user_id == current_user.id):
            return render_template('delete_user.html', template_form=form, user=user)
        else:
            return redirect(url_for('home'))

@app.route('/pass_reset/<int:user_id>', methods=['GET', 'POST'])
@login_required
def pass_reset(user_id):
    """Route for resetting child passwords"""

    form = ChildResetPasswordForm()
    user = User.query.get(user_id)
    
    if request.method == 'POST' and form.validate_on_submit():
        password = form.new_password.data
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        user.password_hash = hash
        db_commit()
        return redirect(url_for('children'))
    
    else:
        if user is not None and user.parent == current_user.id:
            return render_template('pass_reset.html', template_form=form, user=user)
        else:
            return redirect(url_for('children'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('index'))


# Route for testing database inserts and modifications
@app.route('/test')
def test():
    # new_notification1 = Notification(type='Reward', message='Child has requested reward', parent_id=3, child_id = 4)
    # new_notification2 = Notification(type='Chore', message='Child says they have finished chore', parent_id=3, child_id = 4)

    # db.session.add(new_notification1)
    # db.session.add(new_notification2)
    # try:
    #     db.session.commit()
    #     print("Commit successful")
    # except:
    #     db.session.rollback()
    #     print("Commit failed")
    # return redirect(url_for('index'))
    pass



