from flask import redirect, render_template, request, Blueprint, flash
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash

from .forms import (AssignedChoreForm, RewardForm, ChildRegForm, PointsForm,
    ChoreForm, ParentResetPasswordForm)
from .sql_models import (db, Child, AssignedChore, Chore, Reward,
    ParentNotification, ChildNotification)
from .helpers import (db_commit, redirect_url, register_child, flash_errors,
    approve_completed, reject_completed, create_chore, assign_chore, edit_chore,
    create_reward, edit_reward)

parent_bp = Blueprint('parent', __name__, url_prefix="/parent")

@parent_bp.route('/home')
@login_required
def home():
    """Parents homepage"""

    parent = current_user
    child_data = []
    # Get list of notifications for user
    notifications = parent.notifications
    chore_form = AssignedChoreForm()
    reward_form = RewardForm()

    # Create list of dictionaries of data for children
    # and count of the chores assigned to them
    for child in parent.children:
        chores = child.assigned_chores.count()
        child_dict = {'username': child.username, 'first_name': child.first_name,
        'points': child.points, 'chores': chores}
        child_data.append(child_dict)
    return render_template('parents/home.html', child_data=child_data,
        notifications=notifications, chore_form=chore_form, reward_form=reward_form)

@parent_bp.route('/children', methods=['GET', 'POST'])
@login_required
def children():
    """Parent's children page for listing and creating child accounts"""

    register_form = ChildRegForm()
    points_form = PointsForm()
    chore_form = AssignedChoreForm()

    if request.method == 'POST':
        # Register new child account
        if register_form.validate() and register_form.submit.data:
            username = register_form.username.data
            password = register_form.password.data
            first_name = register_form.first_name.data
            register_child(username, password, first_name)
            flash(f'Account created for {first_name}', 'success')
            db_commit()
            return redirect(redirect_url())

        # Adjust child's points
        if points_form.validate() and points_form.adjust.data:
            child = Child.query.get(points_form.child_id.data)
            new_points = points_form.points.data
            child.points += new_points
            if new_points < 0:
                new_points = -new_points
                flash(f"{new_points} points removed from {child.first_name}'s account.",
                    'success')
            else:
                flash(f"{new_points} points added to {child.first_name}'s account.",
                    'success')
            db_commit()
            return redirect(redirect_url())

        # Check if chore_form is being submitted
        if (chore_form.validate() and (chore_form.delete.data
            or chore_form.approve.data or chore_form.reject.data)):

            current_chore = AssignedChore.query.get(chore_form.chore_id.data)
            chore_info = Chore.query.get(current_chore.chore_id)
            child = Child.query.get(current_chore.user_id)

            # Approve completed chore, assign points, and delete assigned chore
            if chore_form.approve.data:
                new_points = chore_info.value
                approve_completed(current_chore, child, new_points)
                flash(f'{chore_info.name} complete!', 'success')

            # Delete assigned chore
            elif chore_form.delete.data:
                db.session.delete(current_chore)
                flash(f'{chore_info.name} has been removed for {child.first_name}', 'success')

            # Reject completed chore, and set status back to active
            elif chore_form.reject.data:
                reject_completed(current_chore)
                flash(f'{chore_info.name} has been sent back to {child.first_name}', 'success')
            db_commit()
            return redirect(redirect_url())

        flash_errors(register_form)
        flash_errors(chore_form)
        return redirect(redirect_url())

    children = current_user.children
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
            'points': child.points, 'id': child.id, 'chores': chores, 'count': len(chores)}

        child_data.append(child_dict)

    return render_template('parents/children.html', template_form=register_form,
    points_form=points_form, chore_form=chore_form, child_data=child_data)

@parent_bp.route('/chores', methods=['GET', 'POST'])
@login_required
def parent_chores():
    """Parent's chore page for creating, viewing, editing, and assigning chores"""

    parent = current_user
    child_count = parent.children.count()
    form = ChoreForm()

    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        value = form.value.data
        child = Child.query.get(form.child.data)
        chore_id = form.chore_id.data
        chore = Chore.query.get(chore_id)

        # Create new chore
        if form.create.data:
            create_chore(name, value, parent.id)

        # Assign chore to child
        elif form.assign.data:
            assign_chore(chore_id, child.id)
            flash(f'{chore.name} assigned to {child.first_name}', 'success')

        # Edit existing chore
        elif form.edit.data:
            edit_chore(chore, name, value)
            flash(f'{chore.name} has been updated', 'success')

        # Delete chore
        elif form.delete.data:
            db.session.delete(chore)
        db_commit()
        return redirect(redirect_url())

    flash_errors(form)
    chores = parent.chores.order_by(Chore.name)
    return render_template('parents/chores.html', template_form=form, chores=chores, child_count=child_count)

@parent_bp.route('/rewards', methods=['GET', 'POST'])
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
        elif form.deliver.data:
            notification = ParentNotification.query.get(form.notification_id.data)
            db.session.delete(notification)
            message = f'You have been given {reward.name}!'
            new_notification = ChildNotification(type='reward', message=message,
                child_id=notification.child_id, reward_id=notification.reward_id)
            db.session.add(new_notification)
            flash('Reward delivered', 'success')
        db_commit()
        return redirect(redirect_url())

    flash_errors(form)
    rewards = parent.rewards.order_by(Reward.name)
    return render_template('parents/rewards.html', template_form=form,
    rewards=rewards)

@parent_bp.route('/settings', methods=['POST', 'GET'])
@login_required
def settings():
    """Parent's settings page"""

    parent = current_user
    form = ParentResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        old_password = form.old_password.data
        if check_password_hash(parent.password_hash, old_password):
            new_password = form.new_password.data
            new_hash = generate_password_hash(new_password,
                method='pbkdf2:sha256', salt_length=8)

            parent.password_hash = new_hash
            db_commit()
            flash('Password changed','success')
        else:
            flash('Please enter correct old password.', 'error')
        return redirect(redirect_url())

    flash_errors(form)
    return render_template('parents/settings.html', parent=parent, template_form=form)
