from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_mail import Mail
from flask_moment import Moment

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
fa = FontAwesome(app)
bootstrap = Bootstrap(app)
login = LoginManager(app)
mail = Mail(app)
moment = Moment(app)

login.login_view = 'login'
login.login_message = 'Aby przejść na tą stronę musisz się najpierw zalogować jako nauczyciel'
login.login_message_category = 'warning'

from app import routes, models, sample_data

db.create_all()
sample_data.initialize()


@login.user_loader
def load_user(user_id):
    return models.Teacher.query.filter_by(id=user_id).first()
