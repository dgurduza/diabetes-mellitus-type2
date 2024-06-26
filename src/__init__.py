from decouple import config
from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object(config("APP_SETTINGS"))

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
migrate = Migrate(app, db)

login_manager = LoginManager() 
login_manager.init_app(app)
login_manager.login_view = "accounts.login"
login_manager.login_message_category = "danger"

from src.calculator.views import calculator_bp
from src.accounts.views import accounts_bp
from src.core.views import core_bp

app.register_blueprint(calculator_bp)
app.register_blueprint(accounts_bp)
app.register_blueprint(core_bp)
