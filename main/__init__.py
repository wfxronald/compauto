from flask import Flask
from .config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager
from flask_moment import Moment

db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
login = LoginManager()
login.login_view = 'auth.login'
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    from main.admin import admin_bp
    from main.auth import auth_bp
    from main.dash import dash_bp
    from main.docs import docs_bp
    from main.opp import opp_bp
    from main.req import req_bp

    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dash_bp, url_prefix='/dash')
    app.register_blueprint(docs_bp, url_prefix='/docs')
    app.register_blueprint(opp_bp, url_prefix='/opp')
    app.register_blueprint(req_bp)

    return app


from main import models
