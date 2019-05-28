from flask import render_template, flash, redirect, url_for, request
from main import app, db
from main.forms import LoginForm, MainForm
from flask_login import current_user, login_user, logout_user, login_required
from main.models import User, Request, Opportunity
from werkzeug.urls import url_parse
from datetime import datetime
from flask_table import Table, Col


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = MainForm()

    form.created_by_name.choices = [(g.staff_name, g.staff_name) for g in User.query.order_by('staff_name')]
    form.closed_by_name.choices = [(g.staff_name, g.staff_name) for g in User.query.order_by('staff_name')]
    form.assign_to_name.choices = [(g.staff_name, g.staff_name) for g in User.query.order_by('staff_name')]

    # Maintain consistent ordering with the choices for staff name
    form.created_by_id.choices = [(g.staff_id, g.staff_id) for g in User.query.order_by('staff_name')]
    form.closed_by_id.choices = [(g.staff_id, g.staff_id) for g in User.query.order_by('staff_name')]
    form.assign_to_id.choices = [(g.staff_id, g.staff_id) for g in User.query.order_by('staff_name')]

    def add_empty_name(choices):
        choices.insert(0, ("", "<Please Select>"))  # The empty option is the first option, i.e. default option

    add_empty_name(form.created_by_name.choices)
    add_empty_name(form.closed_by_name.choices)
    add_empty_name(form.assign_to_name.choices)

    def add_empty_id(choices):
        choices.insert(0, ("", "<Select Name Above>"))  # The empty option is the first option, i.e. default option

    add_empty_id(form.created_by_id.choices)
    add_empty_id(form.closed_by_id.choices)
    add_empty_id(form.assign_to_id.choices)

    current_time = datetime.utcnow()

    if form.validate_on_submit():
        req = Request(requester_name=current_user.staff_name,
                      requester_id=current_user.staff_id,
                      requester_designation=current_user.staff_designation,
                      request_date=current_time,

                      crm_app_no=form.crm_app_no.data,
                      fna_no=form.fna_no.data,

                      created_by_name=form.created_by_name.data,
                      created_by_id=form.created_by_id.data,
                      create_date=form.create_date.data,

                      closed_by_name=form.closed_by_name.data,
                      closed_by_id=form.closed_by_id.data,
                      close_date=form.close_date.data,

                      assign_to_name=form.assign_to_name.data,
                      assign_to_id=form.assign_to_id.data,

                      pdt_name=form.pdt_name.data)

        db.session.add(req)
        db.session.commit()

        flash("Congratulations, your request has been stored in the database")
        return redirect(url_for('index'))

    return render_template('index.html', title='Home', form=form, current_time=current_time)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, cannot login anymore
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(staff_id=form.staff_id.data).first()

        # Check if user has been registered and if the password matches
        if user is None or not user.check_password(form.password.data):
            flash('Invalid staff ID or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # Redirect to index if full URL is included to make the application more secure
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/dashboard')
# Should check if you have permission before allowing access
def dashboard():
    requests = Request.query.all()

    # Declaration of the request table to be presented in HTML form
    class RequestTable(Table):
        id = Col('id')

        requester_name = Col('requester_name')
        requester_id = Col('requester_id')
        requester_designation = Col('requester_designation')
        request_date = Col('request_date')

        crm_app_no = Col('crm_app_no')
        fna_no = Col('fna_no')

        created_by_name = Col('created_by_name')
        created_by_id = Col('created_by_id')
        create_date = Col('create_date')

        closed_by_name = Col('closed_by_name')
        closed_by_id = Col('closed_by_id')
        close_date = Col('close_date')

        assign_to_name = Col('assign_to_name')
        assign_to_id = Col('assign_to_id')

        pdt_name = Col('pdt_name')

    request_table = RequestTable(requests)
    return render_template('dashboard.html', request_table=request_table)


@app.route('/opportunity')
def opportunity():
    opp = Opportunity.query.all()

    # Declaration of the opportunity table to be presented in HTML form
    class OppTable(Table):
        crm_app_no = Col('crm_app_no')
        fna_no = Col('fna_no')

        created_by_name = Col('created_by_name')
        created_by_id = Col('created_by_id')
        create_date = Col('create_date')

        closed_by_name = Col('closed_by_name')
        closed_by_id = Col('closed_by_id')
        close_date = Col('close_date')

        assign_to_name = Col('assign_to_name')
        assign_to_id = Col('assign_to_id')

        pdt_name = Col('pdt_name')

    opp_table = OppTable(opp)
    return render_template('opportunity.html', opp_table=opp_table)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
