from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from main.models import User, Request, Opportunity, Team
from datetime import datetime, timezone
from flask_table import Table, Col, ButtonCol
from main.dash import dash_bp
from main import db


@dash_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    requests = Request.query.order_by(Request.is_approved_by_teamlead,
                                      Request.is_approved_by_teammanager,
                                      Request.is_approved_by_saleshead,
                                      Request.request_date)  # Sort by date to prioritise by urgency -> oldest on top

    # TODO: Must find a way to show approve button only when the user can approve

    # Declaration of the request table to be presented in HTML form
    class LocalTimeCol(Col):
        def td_format(self, content):
            if content:
                adjust_timezone = content.replace(tzinfo=timezone.utc).astimezone(tz=None)
                return adjust_timezone.strftime("%d %b %Y %H:%M:%S")
            else:
                return ''

    class RequestTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        approve_button = ButtonCol('Approve', 'dash.approve', url_kwargs=dict(id='id'),
                                   button_attrs={'class': 'btn btn-success'})

        id = Col('id')
        crm_app_no = Col('crm_app_no')
        reason = Col('reason')

        requester_name = Col('requester_name')
        requester_id = Col('requester_id')
        requester_designation = Col('requester_designation')
        request_date = LocalTimeCol('request_date')

        closed_by_name = Col('closed_by_name')
        closed_by_id = Col('closed_by_id')

        assign_to_name = Col('assign_to_name')
        assign_to_id = Col('assign_to_id')

        is_approved_by_teamlead = Col('is_approved_by_teamlead')
        approving_teamlead_name = Col('approving_teamlead_name')
        approving_teamlead_id = Col('approving_teamlead_id')
        teamlead_approve_date = LocalTimeCol('teamlead_approve_date')

        is_approved_by_teammanager = Col('is_approved_by_teammanager')
        approving_teammanager_name = Col('approving_teammanager_name')
        approving_teammanager_id = Col('approving_teammanager_id')
        teammanager_approve_date = LocalTimeCol('teammanager_approve_date')

        is_approved_by_saleshead = Col('is_approved_by_saleshead')
        approving_saleshead_name = Col('approving_saleshead_name')
        approving_saleshead_id = Col('approving_saleshead_id')
        saleshead_approve_date = LocalTimeCol('saleshead_approve_date')

        def get_tr_attrs(self, item):
            if item.is_approved_by_saleshead:
                return {'class': 'table-success'}
            elif item.is_approved_by_teammanager:
                return {'class': 'table-warning'}
            elif item.is_approved_by_teamlead:
                return {'class': 'table-danger'}
            else:
                return {}

    request_table = RequestTable(requests)

    logged_user = User.query.filter_by(staff_id=current_user.staff_id).first()
    if logged_user.permission_lvl == 0:  # Banker cannot see the request dashboard
        flash('You have no permission to access this page.')
        return redirect(url_for('req.index'))

    return render_template('dash/dashboard.html', title='Request Dashboard', request_table=request_table)


@dash_bp.route('/approve', methods=['POST'])
@login_required
def approve():
    req_id = request.args.get('id')

    req_to_be_approved = Request.query.filter_by(id=req_id).first()
    crm_identifier = req_to_be_approved.crm_app_no
    opp_to_be_changed = Opportunity.query.filter_by(CRM_Appln_No=crm_identifier).first()

    def can_approve(req):
        user_team = current_user.team
        if not req.is_approved_by_teamlead:
            requester_team = User.query.filter_by(staff_id=req.requester_id).first().team
        elif not req.is_approved_by_teammanager:
            requester_team = User.query.filter_by(staff_id=req.approving_teamlead_id).first().team
        else:  # Waiting to be approved by sales head, or already fully approved
            requester_team = User.query.filter_by(staff_id=req.approving_teammanager_id).first().team

        if user_team is None or requester_team is None:  # Admin forgets to assign a staff to a team
            return None

        approver = Team.query.filter_by(from_team=requester_team).first()
        if approver is None:  # Admin forgets to create a relationship between two teams
            return None
        approver_team = approver.to_team

        return user_team == approver_team

    # Modify the request table to indicate approval
    # Currently hard-coded since the flow is likely to be fixed
    role = current_user.staff_designation

    if role == 'Team Lead':
        if req_to_be_approved.is_approved_by_teamlead:
            flash('The request has been approved by Team Lead previously.')
            return redirect(url_for('dash.dashboard'))

        if can_approve(req_to_be_approved) is None:  # If admin forgets to set up, let user know
            flash('An error has occurred on the administrator side. Please contact the administrator!')
            return redirect(url_for('dash.dashboard'))
        elif not can_approve(req_to_be_approved):  # Check that team lead can only approve banker below him/her
            flash('You are not authorised to approve this request. Check again if you are approving the right request!')
            return redirect(url_for('dash.dashboard'))

        # Indicate approval by Team Lead
        req_to_be_approved.is_approved_by_teamlead = True
        req_to_be_approved.approving_teamlead_name = current_user.staff_name
        req_to_be_approved.approving_teamlead_id = current_user.staff_id
        req_to_be_approved.teamlead_approve_date = datetime.utcnow()
        flash('You have approved this appeal. Appeal is now pending for Team Manager approval.')
        db.session.commit()

    elif role == 'Team Manager':
        if not req_to_be_approved.is_approved_by_teamlead:
            flash('The request has not been approved by a Team Lead. Please wait for Team Lead\'s approval.')
            return redirect(url_for('dash.dashboard'))
        elif req_to_be_approved.is_approved_by_teammanager:
            flash('The request has been approved by Team Manager previously.')
            return redirect(url_for('dash.dashboard'))

        if can_approve(req_to_be_approved) is None:  # If admin forgets to set up, let user know
            flash('An error has occurred on the administrator side. Please contact the administrator!')
            return redirect(url_for('dash.dashboard'))
        elif not can_approve(req_to_be_approved):  # Check that team manager can only approve team lead below him/her
            flash('You are not authorised to approve this request. Check again if you are approving the right request!')
            return redirect(url_for('dash.dashboard'))

        # Indicate approval by Team Manager
        req_to_be_approved.is_approved_by_teammanager = True
        req_to_be_approved.approving_teammanager_name = current_user.staff_name
        req_to_be_approved.approving_teammanager_id = current_user.staff_id
        req_to_be_approved.teammanager_approve_date = datetime.utcnow()
        flash('You have approved this appeal. Appeal is now pending for Sales Head approval.')
        db.session.commit()

    elif role == 'Sales Head':
        if not req_to_be_approved.is_approved_by_teamlead:
            flash('The request has not been approved by a Team Lead. Please wait for Team Lead\'s approval.')
            return redirect(url_for('dash.dashboard'))
        elif not req_to_be_approved.is_approved_by_teammanager:
            flash('The request has not been approved by a Team Manager. Please wait for Team Manager\'s approval.')
            return redirect(url_for('dash.dashboard'))
        elif req_to_be_approved.is_approved_by_saleshead:
            flash('The request has been approved before. Cannot approve a request twice!')
            return redirect(url_for('dash.dashboard'))

        if can_approve(req_to_be_approved) is None:  # If admin forgets to set up, let user know
            flash('An error has occurred on the administrator side. Please contact the administrator!')
            return redirect(url_for('dash.dashboard'))
        elif not can_approve(req_to_be_approved):  # Check that sales head can only approve team manager below him/her
            flash('You are not authorised to approve this request. Check again if you are approving the right request!')
            return redirect(url_for('dash.dashboard'))

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

    elif role == 'Account Manager':
        flash('You are not allowed to approve any appeal. Proceed to Account Manager to manage accounts instead.')
        return redirect(url_for('dash.dashboard'))

    return redirect(url_for('dash.dashboard'))
