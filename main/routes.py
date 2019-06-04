from flask import render_template, flash, redirect, url_for, request, jsonify
from main import app, db
from main.forms import LoginForm, MainForm, ApproveForm, AccountManagerForm
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

    form.closed_by_name.choices = [(g.staff_name, g.staff_name) for g in User.query.order_by('staff_name')]
    form.assign_to_name.choices = [(g.staff_name, g.staff_name) for g in User.query.order_by('staff_name')]

    # Maintain consistent ordering with the choices for staff name
    form.closed_by_id.choices = [(g.staff_id, g.staff_id) for g in User.query.order_by('staff_name')]
    form.assign_to_id.choices = [(g.staff_id, g.staff_id) for g in User.query.order_by('staff_name')]

    def add_empty_name(choices):
        choices.insert(0, ("", "<Please Select>"))  # The empty option is the first option, i.e. default option

    add_empty_name(form.reason.choices)
    add_empty_name(form.closed_by_name.choices)
    add_empty_name(form.assign_to_name.choices)

    def add_empty_id(choices):
        choices.insert(0, ("", "<Select Name Above>"))  # The empty option is the first option, i.e. default option

    add_empty_id(form.closed_by_id.choices)
    add_empty_id(form.assign_to_id.choices)

    current_time = datetime.utcnow()

    if form.validate_on_submit():
        req = Request(requester_name=current_user.staff_name,
                      requester_id=current_user.staff_id,
                      requester_designation=current_user.staff_designation,
                      request_date=current_time,

                      crm_app_no=form.crm_app_no.data,
                      reason=form.reason.data,

                      closed_by_name=form.closed_by_name.data,
                      closed_by_id=form.closed_by_id.data,

                      assign_to_name=form.assign_to_name.data,
                      assign_to_id=form.assign_to_id.data,

                      is_approved_by_teamlead=False,
                      is_approved_by_saleshead=False)

        # Use a manual foreign key check rather than one that is ingrained in the database
        foreign_key = form.crm_app_no.data
        opp_referenced = Opportunity.query.filter_by(CRM_Appln_No=foreign_key).first()
        if opp_referenced:
            db.session.add(req)
            db.session.commit()
        else:
            flash('The CRM Application Number you input does not exist in the database')
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
    requests = Request.query.order_by(Request.is_approved_by_teamlead, Request.is_approved_by_saleshead, Request.id)  # Sort by date requested as a form of priority?

    # Declaration of the request table to be presented in HTML form
    class RequestTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        id = Col('id')
        crm_app_no = Col('crm_app_no')
        reason = Col('reason')

        requester_name = Col('requester_name')
        requester_id = Col('requester_id')
        requester_designation = Col('requester_designation')
        request_date = Col('request_date')

        closed_by_name = Col('closed_by_name')
        closed_by_id = Col('closed_by_id')

        assign_to_name = Col('assign_to_name')
        assign_to_id = Col('assign_to_id')

        is_approved_by_teamlead = Col('is_approved_by_teamlead')
        approving_teamlead_name = Col('approving_teamlead_name')
        approving_teamlead_id = Col('approving_teamlead_id')
        teamlead_approve_date = Col('teamlead_approve_date')

        is_approved_by_saleshead = Col('is_approved_by_saleshead')
        approving_saleshead_name = Col('approving_saleshead_name')
        approving_saleshead_id = Col('approving_saleshead_id')
        saleshead_approve_date = Col('saleshead_approve_date')

        def get_tr_attrs(self, item):
            if item.is_approved_by_teamlead and item.is_approved_by_saleshead:
                return {'class': 'table-success'}
            elif item.is_approved_by_teamlead:
                return {'class': 'table-warning'}
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

        crm_identifier = req_to_be_approved.crm_app_no
        opp_to_be_changed = Opportunity.query.filter_by(CRM_Appln_No=crm_identifier).first()

        if not opp_to_be_changed:  # This problem would have been overcome by the foreign key constraint
            flash('There is no opportunity with the specified CRM Application number.')
            return redirect(url_for('dashboard'))

        # Modify the request table to indicate approval
        # Two-layered: depends on who is issuing approval
        role = current_user.staff_designation

        if role == "Team Lead":
            if req_to_be_approved.is_approved_by_teamlead and req_to_be_approved.is_approved_by_saleshead:
                flash('The request has been approved previously. Cannot approve a request twice!')
                return redirect(url_for('dashboard'))
            elif req_to_be_approved.is_approved_by_teamlead:
                flash('The request has been approved by Team Lead previously. Please push your Sales Head to approve.')
                return redirect(url_for('dashboard'))

            # Indicate approval by Team Lead
            req_to_be_approved.is_approved_by_teamlead = True
            req_to_be_approved.approving_teamlead_name = current_user.staff_name
            req_to_be_approved.approving_teamlead_id = current_user.staff_id
            req_to_be_approved.teamlead_approve_date = datetime.utcnow()
            flash('You have approved this appeal. Appeal is now pending for Sales Head approval.')
            db.session.commit()

        elif role == "Sales Head":
            if not req_to_be_approved.is_approved_by_teamlead:
                flash('The request has not first been approved by a Team Lead. Please wait for Team Lead\'s approval.')
                return redirect(url_for('dashboard'))
            elif req_to_be_approved.is_approved_by_saleshead:
                flash('The request has been approved previously. Cannot approve a request twice!')
                return redirect(url_for('dashboard'))

            # Indicate approval by Sales Head
            req_to_be_approved.is_approved_by_saleshead = True
            req_to_be_approved.approving_saleshead_name = current_user.staff_name
            req_to_be_approved.approving_saleshead_id = current_user.staff_id
            req_to_be_approved.saleshead_approve_date = datetime.utcnow()

            # Modify the opportunity database depending on the reason
            reason = req_to_be_approved.reason
            if reason == "late":  # If late, no need to change close date -> just match the opp
                opp_to_be_changed.Match = "Y"

            elif reason == "forget":  # Match the opp, but also update the close details
                opp_to_be_changed.Match = "Y"
                opp_to_be_changed.Close_date = datetime.utcnow()  # Just close it today
                opp_to_be_changed.Closed_by_ID = req_to_be_approved.closed_by_id
                opp_to_be_changed.Closed_by_name = req_to_be_approved.closed_by_name

            elif reason == "assign":  # Just change the assign details
                opp_to_be_changed.Assign_to_ID = req_to_be_approved.assign_to_id
                opp_to_be_changed.Assign_to_name = req_to_be_approved.assign_to_name

            elif reason == "decline":  # Remove the match, but also update the decline details
                opp_to_be_changed.Match = None
                opp_to_be_changed.Match_Amt = None
                opp_to_be_changed.Match_Dt = None
                opp_to_be_changed.Acct_No = None
                opp_to_be_changed.Acct_open_date = None

                opp_to_be_changed.Decline = "Y"
                opp_to_be_changed.Decline_by_ID = current_user.staff_id  # Details will be that of sales head
                opp_to_be_changed.Decline_by_name = current_user.staff_name
                opp_to_be_changed.Decline_date = datetime.utcnow()

            elif reason == "unlock":  # Just need to blank the match
                opp_to_be_changed.Match = None

            # Else, reason is other: to be handled manually. Do nothing

            # Done modifying the opportunity database
            flash('You have approved this appeal. Opportunity database has been modified.')
            db.session.commit()

        return redirect(url_for('dashboard'))
    return render_template('dashboard.html', title='Request Dashboard', request_table=request_table, form=form)


@app.route('/opportunity')
@login_required
def opportunity():
    opp = Opportunity.query.all()

    # Declaration of the opportunity table to be presented in HTML form
    class OppTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        CRM_Appln_No = Col('CRM_Appln_No')
        id = Col('id')

        Cust_Indicator = Col('Cust_Indicator')
        Fullname = Col('Fullname')
        ID_No = Col('ID_No')

        Created_by_name = Col('Created_by_name')
        Created_by_ID = Col('Created_by_ID')
        Create_date = Col('Create_date')

        Closed_by_name = Col('Closed_by_name')
        Closed_by_ID = Col('Closed_by_ID')
        Close_date = Col('Close_date')

        Assign_to_name = Col('Assign_to_name')
        Assign_to_ID = Col('Assign_to_ID')

        Insurance_Ref = Col('Insurance_Ref')

        Product_Name_L1 = Col('Product_Name_L1')
        Product_Name_L2 = Col('Product_Name_L2')
        Product_Name_L3 = Col('Product_Name_L3')
        Product_Code = Col('Product_Code')

        SalesType = Col('SalesType')
        RefNo_Caption = Col('RefNo_Caption')
        Base_Curr_Caption = Col('Base_Curr_Caption')
        Alt_Curr_Caption = Col('Alt_Curr_Caption')
        Opty_Amt_Caption = Col('Opty_Amt_Caption')
        Opty_Amt = Col('Opty_Amt')
        OD_Facility_Amt = Col('OD_Facility_Amt')

        Currency_code = Col('Currency_code')
        AltCurrency_code = Col('AltCurrency_code')

        Opty_Source = Col('Opty_Source')
        Opty_Type = Col('Opty_Type')
        Referral_Code = Col('Referral_Code')
        Referral_Comment = Col('Referral_Comment')

        Match = Col('Match')
        Acct_No = Col('Acct_No')
        Acct_open_date = Col('Acct_open_date')
        Match_Amt = Col('Match_Amt')

        Decline = Col('Decline')
        Decline_by_ID = Col('Decline_by_ID')
        Decline_by_name = Col('Decline_by_name')
        Decline_date = Col('Decline_date')
        Decline_Reason = Col('Decline_Reason')

        Assign_by_ID = Col('Assign_by_ID')
        Assign_by_dt = Col('Assign_by_dt')

        rp_pymt_freq = Col('rp_pymt_freq')
        FD_TENOR = Col('FD_TENOR')
        WEIGHTED_MARGIN = Col('WEIGHTED_MARGIN')
        PRE_RECEIVE = Col('PRE_RECEIVE')
        INTERIM_REV_PTS = Col('INTERIM_REV_PTS')

        Admin_Update = Col('Admin_Update')
        Updated_by_name = Col('Updated_by_name')
        Updated_by_ID = Col('Updated_by_ID')
        Update_date = Col('Update_date')

        Match_Dt = Col('Match_Dt')
        Unmatch_Dt = Col('Unmatch_Dt')

        RevShareTSO = Col('RevShareTSO')
        RevShareRM = Col('RevShareRM')
        INTERIM_REV_PTS_TSO = Col('INTERIM_REV_PTS_TSO')
        RP_Term = Col('RP_Term')
        FNA_No = Col('FNA_No')

        Property_Status = Col('Property_Status')
        Property_Type = Col('Property_Type')

    opp_table = OppTable(opp)
    return render_template('opportunity.html', title='Opportunity Database', opp_table=opp_table)


@app.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.staff_designation != "Administrator":
        flash('You have no permission to access this page.')
        return redirect(url_for('index'))

    users = User.query.all()

    # Declaration of the request table to be presented in HTML form
    class UserTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        id = Col('id')
        staff_id = Col('staff_id')
        staff_name = Col('staff_name')
        staff_designation = Col('staff_designation')
        has_permission = Col('has_permission')

    user_table = UserTable(users)

    # Account manager role:
    # 1) Can add/edit/delete users - also using csv
    # 2) Can reset password
    # 3) Can allocate permission
    form = AccountManagerForm()

    if form.validate_on_submit():
        action = form.operation.data
        if action == "add":
            to_add = User(staff_id=form.staff_id.data,
                          staff_name=form.staff_name.data,
                          staff_designation=form.staff_designation.data,
                          has_permission=int(form.has_permission.data))
            db.session.add(to_add)
            db.session.commit()
            flash('User successfully added.')
            return redirect(url_for('admin'))

        elif action == "edit":
            identifier = form.staff_id.data
            to_edit = User.query.filter_by(staff_id=identifier).first()

            if not to_edit:
                flash('There is no such user. Check the staff ID again!')
                return redirect(url_for('admin'))

            to_edit.staff_name = form.staff_name.data
            to_edit.staff_designation = form.staff_designation.data
            to_edit.has_permission = int(form.has_permission.data)
            db.session.commit()
            flash('User successfully edited.')
            return redirect(url_for('admin'))

        elif action == "delete":
            identifier = form.staff_id.data
            to_delete = User.query.filter_by(staff_id=identifier).first()

            if not to_delete:
                flash('There is no such user. Check the staff ID again!')
                return redirect(url_for('admin'))

            db.session.delete(to_delete)
            db.session.commit()
            flash('User successfully deleted.')
            return redirect(url_for('admin'))

    return render_template('admin.html', title='Account Manager', user_table=user_table, form=form)


@app.route('/logout')
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


@app.route('/receiver', methods=['POST'])
def receiver():
    data = request.get_json()
    crm_app_no = data['crm_app_no']

    selected_opp = Opportunity.query.filter_by(CRM_Appln_No=crm_app_no).first()
    if not selected_opp:
        return jsonify({"success": False})
    opp_serialized = selected_opp.__dict__
    opp_serialized.pop('_sa_instance_state')  # Remove the non-relevant key in the resulting dictionary
    return jsonify({"opp": opp_serialized, "success": True})
