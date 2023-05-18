from logging.config import dictConfig

import os

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_gzip import Gzip

dictConfig({
    'version': 1,
    'formatters': {
        'default': {
            'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': 'ext://flask.logging.wsgi_errors_stream',
            'formatter': 'default'

        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': os.environ.get('LOG_PATH') or 'dg_scenario_database.log',
            'formatter': 'default'

        }
    },
    'root': {
        'level': 'INFO',
        'handlers': ['console', 'file']
    }
})


app = Flask(__name__, static_folder='static')
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL') or 'sqlite:///site.db'
app.config['GZIP_COMPRESS_LEVEL'] = 6
app.config['GZIP_MIN_SIZE'] = 500

db = SQLAlchemy(app)

migrate = Migrate(app, db)
gzip = Gzip(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

from dg_scenario_database import views, models
