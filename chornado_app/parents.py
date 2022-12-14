from flask import redirect, render_template, request, Blueprint, flash
from flask_login import login_required

from .forms import *
from .sql_models import *
from .helpers import *

parents_bp = Blueprint('parents', __name__)

@parents_bp.route('/home')
@login_required
def home():
    """Parents homepage"""
    parent = current_user
# Get list of children belonging to user
    children = User.query.filter_by(parent=parent.id).order_by(User.first_name)        
    child_data = []
    # Get list of notifications for user
    notifications = parent.notifications
    chore_form = AssignedChoreForm()
    reward_form = RewardForm()
    
    # Create list of dictionaries of data for children
    # and count of the chores assigned to them
    for child in children:
        chores = child.assigned_chores.count()
        child_dict = {'username': child.username, 'first_name': child.first_name,
        'points': child.points, 'chores': chores}
        child_data.append(child_dict)
    return render_template('parent_home.html', child_data=child_data,
    notifications=notifications, chore_form=chore_form, reward_form=reward_form)
    
@parents_bp.route('/children', methods=['GET', 'POST'])
@login_required
def children():
    """Parent's children page for listing and creating child accounts"""
    
    parent = current_user
    register_form = RegisterForm()
    chore_form = AssignedChoreForm()
    
    if request.method == 'POST' and register_form.validate_on_submit():
        # Register new child account
        if register_form.submit.data:
            username = register_form.username.data
            password = register_form.password.data
            first_name = register_form.first_name.data
            last_name = register_form.last_name.data
            register_user(username, password, first_name, last_name, "child",
            0, parent.id)
            flash(f'Account created for {first_name}')
            db_commit()
            return redirect(redirect_url())

    elif request.method == 'POST' and chore_form.validate_on_submit():    
        current_chore = AssignedChore.query.get(chore_form.chore_id.data)
        chore_info = Chore.query.get(current_chore.chore_id)
        child = User.query.get(current_chore.user_id)
        
        # Approve completed chore, assign points, and delete assigned chore
        if chore_form.approve.data:
            new_points = Chore.query.get(current_chore.chore_id).value
            approve_completed(current_chore, child, new_points)
            flash(f'{chore_info.name} complete!')
        
        # Delete assigned chore
        elif chore_form.delete.data:
            db.session.delete(current_chore)
            flash(f'{chore_info.name} has been removed for {child.first_name}')
        
        # Reject completed chore, and set status back to active
        elif chore_form.reject.data:
            current_chore.state = 'Active'
            flash(f'{chore_info.name} has been sent back to {child.first_name}')
        db_commit()
        return redirect(redirect_url())
    
    else:
        children = User.query.filter_by(parent=parent.id).order_by(User.first_name)
        child_data = []
        
        # Create list of dictionaries of data for children
        # and the chores assigned to them
        for child in children:
            chores = []
            assigned_chores = child.assigned_chores.order_by(AssignedChore.id)
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

@parents_bp.route('/parent_chores', methods=['GET', 'POST'])
@login_required
def parent_chores():
    """Parent's chore page for creating, viewing, editing, and assigning chores"""
    
    parent = current_user
    form = ChoreForm()
    
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        value = form.value.data
        child = User.query.get(form.child.data)
        chore_id = form.chore_id.data
        chore = Chore.query.get(chore_id)
        
        # Create new chore
        if form.create.data:
            create_chore(name, value, parent.id)
        
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
        chores = parent.chores.order_by(Chore.name)
        return render_template('parent_chores.html', template_form=form, chores=chores)

@parents_bp.route('/parent_rewards', methods=['GET', 'POST'])
@login_required
def parent_rewards():
    """Route for viewing, creating, and editing rewards"""

    parent = current_user
    form = RewardForm()    
        
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        cost = form.cost.data
        reward = Reward.query.get(form.reward_id.data)
        if form.create.data:
            create_reward(name, cost, parent.id)
        elif form.edit.data:
            edit_reward(reward, name, cost)
        elif form.delete.data:
            db.session.delete(reward)
        db_commit()
        return redirect(redirect_url())
    else:
        rewards = parent.rewards.order_by(Reward.name)
        return render_template('parent_rewards.html', template_form=form,
        rewards=rewards)