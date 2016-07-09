from flask import render_template
from flask_security import login_required
from webapp import app


@app.route('/')
@login_required
def index():
    return render_template('index.jinja')
