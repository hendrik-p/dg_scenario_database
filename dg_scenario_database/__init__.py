from logging.config import dictConfig

import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',

    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'

    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']

    }
})

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'

db = SQLAlchemy(app)

from dg_scenario_database import views, models
