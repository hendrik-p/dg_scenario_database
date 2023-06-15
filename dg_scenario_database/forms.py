import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange

from dg_scenario_database.models import User

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class ScenarioSubmissionForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    teaser = StringField('Teaser')
    author = StringField('Author', validators=[DataRequired()])
    current_year = datetime.date.today().year
    year = IntegerField('Year', validators=[NumberRange(1992, current_year)])
    category = SelectField('Scenario category', choices=['Official', 'Shotgun', 'Other'], validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    tags = StringField('Tags')
    submit = SubmitField('Submit')


class EditScenarioForm(FlaskForm):
    scenario_id = IntegerField('ID', validators=[DataRequired()])
    title = StringField('Title', validators=[DataRequired()])
    teaser = StringField('Teaser')
    author = StringField('Author', validators=[DataRequired()])
    current_year = datetime.date.today().year
    year = IntegerField('Year', validators=[NumberRange(1992, current_year)])
    category = SelectField('Scenario category', choices=['Official', 'Shotgun', 'Other'], validators=[DataRequired()])
    url = StringField('URL', validators=[DataRequired()])
    submit = SubmitField('Edit')


class CsvUploadForm(FlaskForm):
    csv_file = FileField(validators=[FileRequired()])
    submit = SubmitField('Upload')

