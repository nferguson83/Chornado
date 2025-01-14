from os import environ, makedirs
from flask import Flask
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect()

def create_app():
    '''Creates flask application session'''

    app = Flask(__name__, instance_relative_config=True)

    # Username for fly.io DB
    dblogin = environ.get('DBLOGIN')
    # Password for fly.io DB
    dbpassword = environ.get('DBPASSWORD')
    # Secret key for CSRF
    secret_key = environ.get('SECRET_KEY')
    # Internal address of fly.io DB
    db_internal = environ.get('DBINTERNAL')
    # Web address of fly.io DB
    db_web = environ.get('DBWEB')

    app.config.from_mapping(
        SECRET_KEY=secret_key,
        SQLALCHEMY_ENGINE_OPTIONS={"pool_pre_ping": True},
        # Connection string for development
        # SQLALCHEMY_DATABASE_URI=f'postgresql://{dblogin}:{dbpassword}@{db_web}:5432',
        # Connection string for production
        SQLALCHEMY_DATABASE_URI=f'postgresql://{dblogin}:{dbpassword}@{db_internal}:5432',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    try:
        makedirs(app.instance_path)
    except OSError:
        pass

    csrf.init_app(app)
    
    from chornado_app.sql_models import db
    db.init_app(app)

    from chornado_app.auth import login_manager
    login_manager.init_app(app)

    from .auth import auth_bp
    app.register_blueprint(auth_bp)

    from .routes import routes_bp
    app.register_blueprint(routes_bp)

    from .parents import parent_bp
    app.register_blueprint(parent_bp)

    from .children import child_bp
    app.register_blueprint(child_bp)

    return app
