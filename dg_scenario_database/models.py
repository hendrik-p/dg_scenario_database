from dg_scenario_database import db

scenario_tag_association = db.Table(
    'scenario_tag_association',
    db.Column('scenario_id', db.Integer, db.ForeignKey('scenarios.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'))
)

class Scenario(db.Model):

    __tablename__ = 'scenarios'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, index=True)
    teaser = db.Column(db.Text)
    author = db.Column(db.String)
    year = db.Column(db.String)
    url = db.Column(db.String)

    tags = db.relationship(
        'Tag',
        secondary=scenario_tag_association,
        back_populates='scenarios'
    )


class Tag(db.Model):

    __tablename__ = 'tags'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)

    scenarios = db.relationship(
        'Scenario',
        secondary=scenario_tag_association,
        back_populates='tags'
    )

