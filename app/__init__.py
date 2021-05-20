from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_fontawesome import FontAwesome
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
fa = FontAwesome(app)
bootstrap = Bootstrap(app)


from app import routes, models