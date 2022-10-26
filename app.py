from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Under Contstruction
@app.route('/')
@app.route('/index')
def contstruction():
    return render_template('construction.html')

import routes