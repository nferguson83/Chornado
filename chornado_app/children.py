from flask import redirect, render_template, request, Blueprint, flash
from flask_login import login_required, current_user

from .forms import (NotificationForm, AssignedChoreForm, RewardForm)
from .sql_models import (db, Parent, AssignedChore, ChildNotification, Chore,
    Reward)
from .helpers import (db_commit, redirect_url, complete_chore, flash_errors,
    request_reward)

child_bp = Blueprint('child', __name__, url_prefix="/child")

@child_bp.route("/home", methods=['Get', 'Post'])
@login_required
def home():
    """Children home page"""

    notification_form = NotificationForm()
    chore_form = AssignedChoreForm()

    if request.method == 'POST':
        if notification_form.validate() and notification_form.acknowledge.data:
            notification_id = notification_form.notification_id.data
            notification = ChildNotification.query.get(notification_id)
            db.session.delete(notification)
            db_commit()

        elif chore_form.validate() and chore_form.complete.data:
            chore_id = chore_form.chore_id.data
            complete_chore(chore_id)
        return redirect(redirect_url())

    child = current_user
    notifications = child.notifications
    chores = []
    assigned_chores = child.assigned_chores.order_by(AssignedChore.id)
    for assigned_chore in assigned_chores:
        chore_info = Chore.query.get(assigned_chore.chore_id)
        chore_dict = {'id': assigned_chore.id, 'name': chore_info.name,
            'points': chore_info.value, 'state': assigned_chore.state}

        chores.append(chore_dict)

    return render_template("children/home.html", child=child, chores=chores,
        notifications=notifications, notification_form=notification_form,
        chore_form=chore_form)

@child_bp.route("/rewards", methods=["GET", "POST"])
@login_required
def rewards():
    """Children rewards page"""

    form =  RewardForm()

    if request.method == 'POST' and form.validate_on_submit():
        reward = Reward.query.get(form.reward_id.data)
        if reward.cost > current_user.points:
            flash('You do not have enough points for this reward', 'error')
            return redirect(redirect_url())

        request_reward(current_user, reward)
        return redirect(redirect_url())

    rewards = Parent.query.get(current_user.parent_id).rewards
    flash_errors(form)
    return render_template("children/rewards.html", rewards=rewards,
        template_form=form)
