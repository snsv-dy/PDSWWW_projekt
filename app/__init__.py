from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
fa = FontAwesome(app)


from app import routes, models