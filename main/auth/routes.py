from flask import render_template, flash, redirect, url_for, request
from main.forms import LoginForm, ChangePasswordForm
from flask_login import current_user, login_user, logout_user, login_required
from main.models import User
from werkzeug.urls import url_parse
from main import db
from main.auth import auth_bp


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, cannot login anymore
    if current_user.is_authenticated:
        return redirect(url_for('req.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(staff_id=form.staff_id.data).first()

        # Check if user has been registered and if the password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid staff ID or password.')
            return redirect(url_for('auth.login'))

        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        # Redirect to index if full URL is included to make the application more secure
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('req.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Sign In', form=form)


@auth_bp.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change', methods=['GET', 'POST'])
@login_required
def change():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        current_user.set_password(form.new_pass.data)
        db.session.commit()
        flash('Password successfully changed.')
        return redirect(url_for('auth.change'))

    return render_template('auth/change.html', title='Change Password', form=form)
