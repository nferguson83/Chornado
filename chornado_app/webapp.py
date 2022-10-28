from . import app
from . import routes
from flask import render_template
from flask_sqlalchemy import SQLAlchemy

# Under Contstruction
@app.route('/')
@app.route('/index')
def contstruction():
    return render_template('construction.html')

