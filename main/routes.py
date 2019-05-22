from flask import render_template, flash, redirect, url_for
from main import app
from main.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': 'Admin'}
    return render_template('index.html', title='Home', user=user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        flash("Login functionality not implemented yet. Sorry, {}".format(form.username.data))
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)
