from flask import json, render_template, request, jsonify, redirect, url_for, flash
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

@app.route('/scenarios', methods=['GET'])
def scenarios():
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
    app.logger.info(f'Tag "{tag_name}" added to scenario "{scenario.title}" by user {current_user.username}')
    return jsonify({'success' : True, 'message' : 'Tag added successfully'})

@app.route('/remove_tag', methods=['POST'])
@login_required
def remove_tag_from_scenario():
    data = request.get_json()
    tag_name = data['tag']
    scenario_id = data['scenario_id']
    tag = Tag.query.filter_by(name=tag_name).first()
    scenario = Scenario.query.filter(Scenario.id == scenario_id).first()
    if tag in scenario.tags:
        scenario.tags.remove(tag)
        db.session.commit()
        app.logger.info(f'Tag "{tag_name}" removed from scenario "{scenario.title}" by user {current_user.username}')
        return jsonify({'success' : True, 'message' : 'Tag removed successfully'})
    app.logger.info(f'Could not remove tag "{tag_name}" from scenario "{scenario.title}". Tag not in scenario tag list.')
    return jsonify({'success' : False, 'message' : 'Failed to remove tag'})

@app.route('/remove_tag_from_database', methods=['POST'])
@login_required
def remove_tag_from_database():
    data = request.get_json()
    tag_id = data['tag_id']
    tag_name = data['tag_name']
    Tag.query.filter_by(id=tag_id).delete()
    db.session.commit()
    app.logger.info(f'Tag "{tag_name}" removed from database by user {current_user.username}')
    return jsonify({'success' : True, 'message' : 'Tag removed successfully from database'})

@app.route('/tags')
def browse_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template('tags.html', tags=tags)

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
@login_required
def logout():
    username = current_user.username
    logout_user()
    app.logger.info(f'Logged out user: {username}')
    return redirect(url_for('index'))

@app.route('/check_login', methods=['GET'])
def check_login():
    return jsonify(logged_in=current_user.is_authenticated)

@app.route('/get_tags', methods=['GET'])
def get_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    tag_names = [tag.name for tag in tags]
    return jsonify(tags=tag_names)

@app.route('/tag_table_config', methods=['GET'])
def get_tag_table_config():
    config = {
        'order': [[1, 'asc']],
        'pageLength': -1,
        'lengthMenu': [ [20, 50, 100, -1], [20, 50, 100, 'All'] ],
        'columns': [
            {'data': 'id', 'visible': False},
            {'data': 'tag'},
            {'data': 'scenarios'},
        ]
    }
    if hasattr(current_user, 'is_admin') and current_user.is_admin:
        config['columns'].append({'data': 'button'})
    return jsonify(config)

