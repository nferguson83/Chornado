from os import environ, makedirs
from flask import Flask
from dotenv import load_dotenv

def create_app():
    '''Creates flask application session'''

    app = Flask(__name__, instance_relative_config=True)
    # Load environment variables into OS, and remove .env for production
    load_dotenv('../.env')

    dblogin = environ.get('DBLOGIN')
    dbpassword = environ.get('DBPASSWORD')
    dbdir = environ.get('DBDIR')
    dbwpassword = environ.get('DBWPASSWORD')

    app.config.from_mapping(
        SECRET_KEY='dev', # Change to more secure key
        SQLALCHEMY_DATABASE_URI=f'oracle+oracledb://{dblogin}:{dbpassword}@chornadodb_high/?config_dir={dbdir}&wallet_location={dbdir}&wallet_password={dbwpassword}&encoding=UTF-8&nencoding=UTF-8',
        SQLALCHEMY_TRACK_MODIFICATIONS=False
    )

    try:
        makedirs(app.instance_path)
    except OSError:
        pass

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
