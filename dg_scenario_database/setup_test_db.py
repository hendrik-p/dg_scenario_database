from dg_scenario_database import app, db
from dg_scenario_database.models import Scenario, Tag

with app.app_context():

    db.create_all()

    # Create some tags
    tag1 = Tag(name='Adventure')
    tag2 = Tag(name='Mystery')
    tag3 = Tag(name='Horror')

    # Add the tags to the session and commit them to the database
    db.session.add_all([tag1, tag2, tag3])
    db.session.commit()

    # Create some scenarios and associate them with tags
    scenario1 = Scenario(title='The Lost Temple', teaser='An archaeological adventure', author='John Smith', tags=[tag1])
    scenario2 = Scenario(title='The Missing Heir', teaser='A detective mystery', author='Jane Doe', tags=[tag2])
    scenario3 = Scenario(title='The Haunted Mansion', teaser='A supernatural horror', author='John Smith', tags=[tag3])
    scenario4 = Scenario(title='The Secret Island', teaser='A swashbuckling adventure', author='Jane Doe', tags=[tag1, tag2])

    # Add the scenarios to the session and commit them to the database
    db.session.add_all([scenario1, scenario2, scenario3, scenario4])
    db.session.commit()

