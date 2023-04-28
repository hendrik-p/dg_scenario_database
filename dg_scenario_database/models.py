from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

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


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, server_default='0', nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'
