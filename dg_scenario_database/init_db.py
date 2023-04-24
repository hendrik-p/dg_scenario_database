import json

from dg_scenario_database import app, db
from dg_scenario_database.models import Scenario, Tag

scenario_data = json.load(open('shotgun_scenarios_merged.json'))

with app.app_context():
    db.create_all()
    scenarios = []
    tags = {}
    for scenario in scenario_data:
        title = scenario['title']
        author = scenario['author']
        year = scenario['year']
        url = scenario['url']
        teaser = scenario['teaser']
        assoc_tags = scenario['tags']
        scenario_tags = []
        for tag in assoc_tags:
            if tag in tags:
                tag_obj = tags[tag]
            else:
                tag_obj = Tag(name=tag)
                tags[tag] = tag_obj
            scenario_tags.append(tag_obj)
        scenario = Scenario(
            title=title,
            teaser=teaser,
            author=author,
            year=year,
            url=url,
            tags=scenario_tags
        )
        scenarios.append(scenario)
    tags = [tag for _, tag in tags.items()]
    db.session.add_all(tags)
    db.session.commit()

    db.session.add_all(scenarios)
    db.session.commit()

