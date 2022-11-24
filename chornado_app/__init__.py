from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from dotenv import load_dotenv
from os import environ

app = Flask(__name__)

# Load environment variables into OS, and remove .env for production
load_dotenv('../.env')

dblogin = environ.get('DBLOGIN')
dbpassword = environ.get('DBPASSWORD')
dbdir = environ.get('DBDIR')
dbwpassword = environ.get('DBWPASSWORD')

app.config['SQLALCHEMY_DATABASE_URI'] = f'oracle+oracledb://{dblogin}:{dbpassword}@chornadodb_high/?config_dir={dbdir}&wallet_location={dbdir}&wallet_password={dbwpassword}&encoding=UTF-8&nencoding=UTF-8'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config["SECRET_KEY"] = "mysecret" # Change to more secure key

db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)