from flask import redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash

from . import app, db, login_manager
from .forms import AssignedChoreForm, ChoreForm, LoginForm, RegisterForm, DeleteUserForm, ResetPasswordForm
from .sql_models import AssignedChore, Chore, Notification, Reward, User


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))

# Renders splash screen or parent/child home pages
@app.route('/')
@app.route('/index')
def index():
    if not current_user.is_authenticated:
        return render_template('index.html')
    else:
        return redirect(url_for('home'))

# Login page and function
@app.route('/login', methods=['GET', 'POST'])
def login():
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

# Logout function
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# Register page and function
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST' and form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
        new_user = User(username=username, first_name=first_name, last_name=last_name,
        password_hash=hash, type="parent")
        success='Account created. Please login.'
        db.session.add(new_user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return render_template('login.html', template_form=form,
        success=success)
    else:
        return render_template('register.html', template_form=form)
            
# Parent and child dashboard pages
@app.route('/home')
@login_required
def home():
    # If logged in user is type: parent, load parent homepage
    if current_user.type == 'parent':
        parent = current_user.id
        children = User.query.filter_by(parent=parent).order_by(User.first_name)
        child_data = []
        for child in children:
            chores = AssignedChore.query.filter_by(user_id=child.id)
            chores = len([chore.id for chore in chores])
            child_dict = {'username': child.username, 'first_name': child.first_name, 'points': child.points, 'chores': chores}
            child_data.append(child_dict)
        return render_template('parent_home.html', child_data=child_data)
    # If logged in user is type: child, load child homepage
    else:
        return render_template('child_home.html')

# Parent's children page for listing and creating child accounts
@app.route('/children', methods=['GET', 'POST'])
@login_required
def children():
    register_form = RegisterForm()
    chore_form = AssignedChoreForm()
    parent = current_user.id
    children = User.query.filter_by(parent=parent).order_by(User.first_name)
    child_data = []
    for child in children:
        chores = []
        assigned_chores = AssignedChore.query.filter_by(user_id=child.id).order_by(AssignedChore.id)
        for chore in assigned_chores:
            chore_info = Chore.query.get(chore.chore_id)
            chore_dict = {'name': chore_info.name, 'points': chore_info.value, 'status': chore.state}
            chores.append(chore_dict)
        child_dict = {'username': child.username, 'first_name': child.first_name, 'points': child.points, 'chores': chores}
        child_data.append(child_dict)
    if request.method == 'POST' and (register_form.validate_on_submit() or chore_form.validate_on_submit()):
        # Register new child account
        if register_form.submit.data:
            username = register_form.username.data
            password = register_form.password.data
            first_name = register_form.first_name.data
            last_name = register_form.last_name.data
            hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=8)
            new_user = User(username=username, first_name=first_name, last_name=last_name,
            password_hash=hash, type="child", points=0, parent=parent)
            db.session.add(new_user)
        elif chore_form.complete.data:
            pass
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('children'))
    # List of children and their active chores
    else:
        
        return render_template('children.html', template_form=register_form, chore_form=chore_form, child_data=child_data)

# Parent's chore page for creating, viewing, editing, and assigning chores
@app.route('/parent_chores', methods=['GET', 'POST'])
@login_required
def parent_chores():
    parent = current_user.id
    chores = Chore.query.filter_by(parent_id=parent)
    form = ChoreForm()
    if request.method == 'POST' and form.validate_on_submit():
        name = form.name.data
        value = form.value.data
        chore_id = form.chore_id.data
        chore = Chore.query.get(chore_id)
        if form.create.data:
            new_chore = Chore(name=name, value=value, parent_id=parent)
            db.session.add(new_chore)
        elif form.assign.data:
            child = form.child.data
            if AssignedChore.query.filter_by(user_id=child, chore_id=chore_id).count() > 0:
                print('duplicate entry')
                error = "This chore has already been assigned to this child."
                return render_template('parent_chores.html', template_form=form, chores=chores, error=error)
            else:    
                new_assigned_chore = AssignedChore(state='Active', chore_id=chore_id, user_id=child)
                db.session.add(new_assigned_chore)
        elif form.edit.data:
            chore.name = name
            chore.value = value
        elif form.delete.data:
            db.session.delete(chore)
        try:
            db.session.commit()
            print('commit successful')
        except:
            db.session.rollback()
            print('commit fail')
        return redirect(url_for('parent_chores', template_form=form))
    else:
        return render_template('parent_chores.html', template_form=form, chores=chores)

# Route for deleting users
@app.route('/delete/<int:user_id>', methods=['GET', 'POST'])
def delete_user(user_id):
    form = DeleteUserForm()
    user = User.query.get(user_id)
    if request.method == 'POST' and form.validate_on_submit():
        if user.type == 'parent':
            children = User.query.filter_by(parent=user.id).all()
            for child in children:
                db.session.delete(child)
            db.session.delete(user)
            logout_user()
        else:
            db.session.delete(user)
        try:
            db.session.commit()
            print('commit successful')
        except:
            db.session.rollback()
            print('commit fail')
        return redirect(url_for('home'))
    else:
        if user.parent == current_user.id or user_id == current_user.id:
            return render_template('delete_user.html', template_form=form, user=user)
        else:
            return redirect(url_for('home'))
        


# Route for testing database inserts and modifications
@app.route('/test')
def test():
    # new_chore = Chore(name='Dishes', value=10, parent_id=1)
    # new_chore = AssignedChore(state='Active', chore_id=2, user_id=2)
    # db.session.add(new_chore)
    # try:
    #     db.session.commit()
    # except:
    #     db.session.rollback()
    return redirect(url_for('index'))

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('index'))

