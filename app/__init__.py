from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
fa = FontAwesome(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)

from app import routes, models, db_sample_data

db.create_all()
db_sample_data.initialize()


@login.user_loader
def load_user(user_id):
    return models.Teacher.query.filter_by(id=user_id).first()
