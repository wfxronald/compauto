from flask import render_template, flash, redirect, url_for, request
from main import app
from main.forms import LoginForm, MockForm, MainForm
from flask_login import current_user, login_user, logout_user, login_required
from main.models import User
from werkzeug.urls import url_parse


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = MockForm()
    main_form = MainForm()
    if form.validate_on_submit():
        flash("Data format is correct, but have not been stored yet")
        return redirect(url_for('index'))
    return render_template('index.html', title='Home', form=form, main_form=main_form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, cannot login anymore
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        # Check if user has been registered and if the password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # Redirect to index if full URL is included to make the application more secure
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
