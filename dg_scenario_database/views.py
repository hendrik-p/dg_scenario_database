from flask import render_template, request, jsonify, redirect, url_for, flash, send_from_directory
from flask_login import login_user, current_user, logout_user, login_required

from dg_scenario_database import app, db, login_manager
from dg_scenario_database.models import Scenario, Tag, Upvote, User
from dg_scenario_database.forms import LoginForm, RegistrationForm, ScenarioSubmissionForm, EditScenarioForm

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# HTML routes

@app.route('/robots.txt')
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(app.static_folder, request.path[1:])

@app.route('/', methods=['GET'])
@app.route('/scenarios', methods=['GET'])
def index():
    scenarios = Scenario.query.all()
    if current_user.is_authenticated:
        upvotes = Upvote.query.filter_by(user_id=current_user.id).all()
        upvote_ids = [upvote.scenario_id for upvote in upvotes]
    else:
        upvote_ids = []
    return render_template('index.html', scenarios=scenarios, upvotes=upvote_ids)

@app.route('/tags')
def browse_tags():
    tags = Tag.query.order_by(Tag.name.asc()).all()
    return render_template('tags.html', tags=tags)

@app.route('/submit_scenario', methods=['GET', 'POST'])
@login_required
def submit_scenario():
    form = ScenarioSubmissionForm()
    if form.validate_on_submit():
        tag_string = form.tags.data
        tag_names = [t.strip() for t in tag_string.split(',') if t.strip()]
        tags = []
        for tag_name in tag_names:
            tag = Tag.query.filter_by(name=tag_name).first()
            if not tag:
                tag = Tag(name=tag_name)
                db.session.add(tag)
                db.session.commit()
            tags.append(tag)
        scenario = Scenario(
            title=form.title.data,
            teaser=form.teaser.data,
            author=form.author.data,
            year=str(form.year.data),
            category=form.category.data,
            url=form.url.data,
            tags=tags
        )
        db.session.add(scenario)
        db.session.commit()
        flash('Scenario submitted!')
        app.logger.info(f'Scenario {scenario.title} added by {current_user.username}')
        return redirect(url_for('submit_scenario'))
    return render_template('submit_scenario.html', form=form)

# login, logout, registration

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

# admin routes

@app.route('/dashboard')
@login_required
def dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    return render_template('dashboard.html')

@app.route('/edit_scenarios', methods=['GET', 'POST'])
@login_required
def edit_scenarios():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    scenarios = Scenario.query.all()
    form = EditScenarioForm()
    if form.validate_on_submit():
        scenario_id = form.scenario_id.data
        scenario = Scenario.query.filter_by(id=scenario_id).first()
        scenario.title = form.title.data
        scenario.teaser = form.teaser.data
        scenario.author = form.author.data
        scenario.year = form.year.data
        scenario.category = form.category.data
        scenario.url = form.url.data
        db.session.commit()
        app.logger.info(f'Scenario {scenario_id} edited by {current_user.username}')
        return render_template('edit_scenarios.html', scenarios=scenarios, form=form)
    return render_template('edit_scenarios.html', scenarios=scenarios, form=form)

@app.route('/edit_tags', methods=['GET', 'POST'])
@login_required
def edit_tags():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    if request.method == 'POST':
        tag_id = request.values.get('tag_id')
        tag_name = request.values.get('tag_name')
        tag = Tag.query.filter_by(id=tag_id).first()
        tag.name = tag_name
        db.session.commit()
    tags = Tag.query.all()
    return render_template('edit_tags.html', tags=tags)

@app.route('/show_users')
def show_users():
    users = User.query.all()
    return render_template('show_users.html', users=users)

# AJAX routes

@app.route('/add_tag', methods=['POST'])
@login_required
def add_tag():
    data = request.get_json()
    tag_name = data['tag']
    tag_name = tag_name.lower()
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

@app.route('/get_scenario', methods=['POST'])
def get_scenario():
    data = request.get_json()
    scenario_id = data['scenario_id']
    scenario = Scenario.query.filter_by(id=scenario_id).first()
    json = jsonify(
        scenario_id=scenario_id,
        title=scenario.title,
        teaser=scenario.teaser,
        author=scenario.author,
        year=scenario.year,
        category=scenario.category,
        url=scenario.url,
    )
    return json

@app.route('/delete_scenario', methods=['POST'])
@login_required
def delete_scenario():
    if not current_user.is_admin:
        return jsonify({'success': False})
    data = request.get_json()
    scenario_id = data['scenario_id']
    Scenario.query.filter_by(id=scenario_id).delete()
    db.session.commit()
    app.logger.info(f'Scenario {scenario_id} deleted by user {current_user.username}')
    return jsonify({'success': True})

@app.route('/vote', methods=['POST'])
@login_required
def vote():
    data = request.get_json()
    scenario_id = data['scenario_id']
    scenario = Scenario.query.filter_by(id=scenario_id).first()
    if data['vote'] == 'add':
        existing = Upvote.query.filter_by(user_id=current_user.id).all()
        for vote in existing:
            if vote.scenario_id == scenario_id:
                return jsonify({'success': False})
        upvote = Upvote(user_id=current_user.id, scenario_id=scenario.id)
        db.session.add(upvote)
        db.session.commit()
        app.logger.info(f'User {current_user.username} voted for scenario {scenario_id}')
    elif data['vote'] == 'remove':
        upvote = Upvote.query.filter_by(user_id=current_user.id, scenario_id=scenario_id)
        if not upvote:
            return jsonify({'success': False})
        upvote.delete()
        db.session.commit()
        app.logger.info(f'User {current_user.username} removed vote for scenario {scenario_id}')
    return jsonify({'success': True})

