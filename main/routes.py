from flask import render_template
from main import app


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Admin'}
    return render_template('index.html', title='Home', user=user)
