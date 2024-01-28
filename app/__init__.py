from flask import Flask
from config import Config
from flask_login import LoginManager

app = Flask(__name__)
app.config.from_object(Config)

login_manager = LoginManager(app)
login_manager.login_message = None 
login_manager.login_view = 'login'

from app.routes import main_routes, auth_routes
from app.models import user
