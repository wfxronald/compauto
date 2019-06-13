from flask import render_template, flash, redirect, url_for, request, jsonify
from main.forms import MainForm
from flask_login import current_user, login_required
from main.models import User, Request, Opportunity
from datetime import datetime
from main import db
from main.req import req_bp


@req_bp.route('/index', methods=['GET', 'POST'])
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
                      is_approved_by_teammanager=False,
                      is_approved_by_saleshead=False)

        db.session.add(req)
        db.session.commit()
        flash("Congratulations, your request has been stored in the database.")
        return redirect(url_for('req.index'))

    return render_template('req/index.html', title='Home', form=form, current_time=current_time)


@req_bp.route('/receiver', methods=['POST'])
def receiver():
    data = request.get_json()
    crm_app_no = data['crm_app_no']

    selected_opp = Opportunity.query.filter_by(CRM_Appln_No=crm_app_no).first()
    if not selected_opp:
        return jsonify({"success": False})
    opp_serialized = selected_opp.__dict__
    opp_serialized.pop('_sa_instance_state')  # Remove the non-relevant key in the resulting dictionary
    return jsonify({"opp": opp_serialized, "success": True})
