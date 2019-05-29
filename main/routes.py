from flask import render_template, flash, redirect, url_for, request
from main import app, db
from main.forms import LoginForm, MainForm, ApproveForm
from flask_login import current_user, login_user, logout_user, login_required
from main.models import User, Request, Opportunity
from werkzeug.urls import url_parse
from datetime import datetime
from flask_table import Table, Col
from sqlalchemy.exc import IntegrityError


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

                      pdt_name=form.pdt_name.data,

                      is_approved=False)

        try:
            db.session.add(req)
            db.session.commit()
        except IntegrityError:
            flash('The CRM Application No you input does not exist in the database')
            return redirect(url_for('index'))

        flash("Congratulations, your request has been stored in the database.")
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
            flash('Invalid staff ID or password.')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)

        next_page = request.args.get('next')
        # Redirect to index if full URL is included to make the application more secure
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')

        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ApproveForm()
    requests = Request.query.order_by(Request.is_approved, Request.id)  # Sort by date requested as a form of priority?

    # Declaration of the request table to be presented in HTML form
    class RequestTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

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

        is_approved = Col('is_approved')
        approved_by_name = Col('approved_by_name')
        approved_by_id = Col('approved_by_id')
        approve_date = Col('approve_date')

        def get_tr_attrs(self, item):
            if item.is_approved:
                return {'class': 'success'}
            else:
                return {}

    request_table = RequestTable(requests)

    logged_user = User.query.filter_by(id=current_user.id).first()
    if not logged_user.has_permission:  # Only admin can access the request dashboard
        flash('You have no permission to access this page.')
        return redirect(url_for('index'))

    if form.validate_on_submit():
        req_to_be_approved = Request.query.filter_by(id=form.req_id.data).first()
        if not req_to_be_approved:
            flash('The request ID you have input is invalid.')
            return redirect(url_for('dashboard'))

        if req_to_be_approved.is_approved:
            flash('The request has been approved previously.')
            return redirect(url_for('dashboard'))

        crm_identifier = req_to_be_approved.crm_app_no
        opp_to_be_changed = Opportunity.query.filter_by(crm_app_no=crm_identifier).first()
        if not opp_to_be_changed:
            flash('There is no opportunity with the specified CRM Application number.')
            return redirect(url_for('dashboard'))

        # Modify the opportunity database
        opp_to_be_changed.fna_no = req_to_be_approved.fna_no

        opp_to_be_changed.created_by_name = req_to_be_approved.created_by_name
        opp_to_be_changed.created_by_id = req_to_be_approved.created_by_id
        opp_to_be_changed.create_date = req_to_be_approved.create_date

        opp_to_be_changed.closed_by_name = req_to_be_approved.closed_by_name
        opp_to_be_changed.closed_by_id = req_to_be_approved.closed_by_id
        opp_to_be_changed.close_date = req_to_be_approved.close_date

        opp_to_be_changed.assign_to_name = req_to_be_approved.assign_to_name
        opp_to_be_changed.assign_to_id = req_to_be_approved.assign_to_id

        opp_to_be_changed.pdt_name = req_to_be_approved.pdt_name

        # Modify the request table to indicate approval
        req_to_be_approved.is_approved = True
        req_to_be_approved.approved_by_name = logged_user.staff_name
        req_to_be_approved.approved_by_id = logged_user.staff_id
        req_to_be_approved.approve_date = datetime.utcnow()

        db.session.commit()

        flash('Congratulations, opportunity database has been successfully modified.')
        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', title='Request Dashboard', request_table=request_table, form=form)


@app.route('/opportunity')
@login_required
def opportunity():
    opp = Opportunity.query.all()

    # Declaration of the opportunity table to be presented in HTML form
    class OppTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

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
    return render_template('opportunity.html', title='Opportunity Database', opp_table=opp_table)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))
