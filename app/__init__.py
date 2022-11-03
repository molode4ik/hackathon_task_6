from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SECRET_KEY'] = 'gegweerhjjkfbidfoboiqoieqoiquyhoosrmkfnlfdn'
login_manager = LoginManager(app)
login_manager.login_view = 'index'

from app import routes
from avito_parser import models
