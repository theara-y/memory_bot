from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from config import Config

db = SQLAlchemy()
login = LoginManager()
bcrypt = Bcrypt()
migrate = Migrate()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    login.init_app(app)
    bcrypt.init_app(app)
    migrate.init_app(app, db)

    from src.auth.routes import bp as auth_routes
    app.register_blueprint(auth_routes)

    from src.app.routes import bp as app_routes
    app.register_blueprint(app_routes)

    return app