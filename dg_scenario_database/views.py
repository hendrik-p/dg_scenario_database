from flask import render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_user, current_user, logout_user, login_required

from dg_scenario_database import app, db, login_manager
from dg_scenario_database.models import Scenario, Tag, User
from dg_scenario_database.forms import LoginForm, RegistrationForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/', methods=['GET'])
def index():
    scenarios = Scenario.query.all()
    return render_template('index.html', scenarios=scenarios)

@app.route('/add_tag', methods=['POST'])
@login_required
def add_tag():
    data = request.get_json()
    tag_name = data['tag']
    scenario_id = data['scenario_id']
    new_tag = Tag.query.filter_by(name=tag_name).first()
    if not new_tag:
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
        app.logger.info(f'Created new tag: "{tag_name}"')
    scenario = Scenario.query.filter(Scenario.id == scenario_id).first()
    scenario.tags.append(new_tag)
    db.session.commit()
    app.logger.info(f'Tag "{tag_name}" added to scenario "{scenario.title}"')
    return jsonify({'success' : True, 'message' : 'Tag added successfully'})

@app.route('/remove_tag', methods=['POST'])
@login_required
def remove_tag():
    data = request.get_json()
    tag_name = data['tag']
    scenario_id = data['scenario_id']
    tag = Tag.query.filter_by(name=tag_name).first()
    scenario = Scenario.query.filter(Scenario.id == scenario_id).first()
    if tag in scenario.tags:
        scenario.tags.remove(tag)
        db.session.commit()
        app.logger.info(f'Tag "{tag_name}" removed from scenario "{scenario.title}"')
        return jsonify({'success' : True, 'message' : 'Tag removed successfully'})
    app.logger.info(f'Could not remove tag "{tag_name}" from scenario "{scenario.title}". Tag not in scenario tag list.')
    return jsonify({'success' : False, 'message' : 'Failed to remove tag'})

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        app.logger.info(f'Registered new user: {user.username}')
        login_user(user, remember=True)
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            app.logger.info(f'Logged in user: {user.username}')
            return redirect(url_for('index'))
        else:
            flash('Login unsuccessful. Please check your username and password.')
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    username = current_user.username
    logout_user()
    app.logger.info(f'Logged out user: {username}')
    return redirect(url_for('index'))

@app.route('/show_tags', methods=['GET'])
def show_tags():
    tags = Tag.query.all()
    out = '\n'.join([tag.name for tag in tags])
    return out

