from flask import render_template, request, jsonify

from dg_scenario_database import app, db
from dg_scenario_database.models import Scenario, Tag

@app.route('/', methods=['GET'])
def index():
    scenarios = Scenario.query.all()
    return render_template('index.html', scenarios=scenarios)

@app.route('/add_tag', methods=['POST'])
def add_tag():
    data = request.get_json()
    tag_name = data['tag']
    scenario_id = data['scenario_id']
    new_tag = Tag.query.filter_by(name=tag_name).first()
    if not new_tag:
        new_tag = Tag(name=tag_name)
        db.session.add(new_tag)
        db.session.commit()
    scenario = Scenario.query.filter(Scenario.id == scenario_id).first()
    scenario.tags.append(new_tag)
    db.session.commit()
    app.logger.info(f'Tag {tag_name} added to scenario {scenario.title}')
    return jsonify({'success' : True, 'message' : 'Tag added successfully'})

@app.route('/remove_tag', methods=['POST'])
def remove_tag():
    data = request.get_json()
    tag_name = data['tag']
    scenario_id = data['scenario_id']
    tag = Tag.query.filter_by(name=tag_name).first()
    scenario = Scenario.query.filter(Scenario.id == scenario_id).first()
    scenario.tags.remove(tag)
    db.session.commit()
    app.logger.info(f'Tag {tag_name} removed from scenario {scenario.title}')
    return jsonify({'success' : True, 'message' : 'Tag removed successfully'})

@app.route('/show_tags', methods=['GET'])
def show_tags():
    tags = Tag.query.all()
    out = '\n'.join([tag.name for tag in tags])
    return out
