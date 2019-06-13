from flask import render_template, flash, redirect, url_for, request
from main.forms import AccountManagerForm, RelationshipForm
from flask_login import current_user, login_required
from main.models import User, Team
from flask_table import Table, Col, ButtonCol
from main import db
from main.admin import admin_bp


@admin_bp.route('/admin', methods=['GET'])
@login_required
def admin():
    if current_user.permission_lvl < 3:
        flash('You have no permission to access this page.')
        return redirect(url_for('req.index'))

    users = User.query.order_by('staff_id')
    teams = Team.query.order_by('id')

    # Declaration of the request table to be presented in HTML form
    class UserTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        edit_button = ButtonCol('Edit', 'admin.edit', button_attrs={'class': 'btn btn-primary'},
                                url_kwargs=dict(staff_id='staff_id'))
        delete_button = ButtonCol('Delete', 'admin.delete', button_attrs={'class': 'btn btn-danger'},
                                  url_kwargs=dict(staff_id='staff_id'))
        reset_button = ButtonCol('Reset Password', 'admin.reset', button_attrs={'class': 'btn btn-warning'},
                                 url_kwargs=dict(staff_id='staff_id'))

        staff_id = Col('staff_id')
        staff_name = Col('staff_name')
        staff_designation = Col('staff_designation')
        permission_lvl = Col('permission_lvl')
        team = Col('team')

    class TeamTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        edit_button = ButtonCol('Edit', 'admin.define', button_attrs={'class': 'btn btn-primary'},
                                url_kwargs=dict(id='id'))
        delete_button = ButtonCol('Delete', 'admin.clear', button_attrs={'class': 'btn btn-danger'},
                                  url_kwargs=dict(id='id'))

        id = Col('id')
        from_team = Col('from_team')
        to_team = Col('to_team')

    user_table = UserTable(users)
    team_table = TeamTable(teams)

    return render_template('admin/admin.html', title='Account Manager', user_table=user_table, team_table=team_table)


@admin_bp.route('/edit', methods=['GET', 'POST'])
@login_required
def edit():
    identifier = request.args.get('staff_id')

    if identifier:
        user_to_edit = User.query.filter_by(staff_id=identifier).first()

        if user_to_edit.permission_lvl == 4:
            flash('To prevent disaster, you cannot edit an Administrator account')
            return redirect(url_for('admin.admin'))

        form = AccountManagerForm(obj=user_to_edit)
        del form.staff_id  # Cannot edit a staff ID
    else:
        form = AccountManagerForm()

    if form.validate_on_submit():
        if not identifier:  # This is an add operation
            to_add = User(staff_id=form.staff_id.data,
                          staff_name=form.staff_name.data,
                          staff_designation=form.staff_designation.data,
                          permission_lvl=int(form.permission_lvl.data),
                          team=form.team.data)
            db.session.add(to_add)
            to_add.set_password('test')  # This is the default password of a newly created account

            db.session.commit()
            flash('User successfully added.')
            return redirect(url_for('admin.admin'))

        else:
            to_edit = User.query.filter_by(staff_id=identifier).first()

            to_edit.staff_name = form.staff_name.data
            to_edit.staff_designation = form.staff_designation.data
            to_edit.permission_lvl = int(form.permission_lvl.data)
            to_edit.team = form.team.data

            db.session.commit()
            flash('User successfully edited.')
            return redirect(url_for('admin.admin'))

    return render_template('admin/edit.html', title='User Manager', form=form)


@admin_bp.route('/delete', methods=['POST'])
@login_required
def delete():
    identifier = request.args.get('staff_id')
    to_delete = User.query.filter_by(staff_id=identifier).first()

    if to_delete.permission_lvl == 4:
        flash('To prevent disaster, you cannot delete an Administrator account')
        return redirect(url_for('admin.admin'))

    db.session.delete(to_delete)
    db.session.commit()
    flash('User successfully deleted.')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/reset', methods=['POST'])
@login_required
def reset():
    identifier = request.args.get('staff_id')
    to_reset = User.query.filter_by(staff_id=identifier).first()

    if to_reset.permission_lvl == 4:
        flash('To prevent disaster, you cannot reset the password of an Administrator account')
        return redirect(url_for('admin.admin'))

    to_reset.set_password('test')  # Back to our default password
    db.session.commit()
    flash('Password successfully reset.')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/clear', methods=['POST'])
@login_required
def clear():
    identifier = request.args.get('id')
    to_delete = Team.query.filter_by(id=identifier).first()
    db.session.delete(to_delete)
    db.session.commit()
    flash('Relationship successfully deleted.')
    return redirect(url_for('admin.admin'))


@admin_bp.route('/define', methods=['GET', 'POST'])
def define():
    identifier = request.args.get('id')

    if identifier:
        form = RelationshipForm(begin=Team.query.filter_by(id=identifier).first().from_team,
                                end=Team.query.filter_by(id=identifier).first().to_team)
    else:
        form = RelationshipForm()

    if form.validate_on_submit():
        if not identifier:  # This is an add operation
            to_add = Team(from_team=form.begin.data, to_team=form.end.data)
            db.session.add(to_add)
            db.session.commit()
            flash('Relationship successfully added.')
            return redirect(url_for('admin.admin'))

        else:  # This is an edit operation
            to_edit = Team.query.filter_by(id=identifier).first()
            to_edit.from_team = form.begin.data
            to_edit.to_team = form.end.data
            db.session.commit()
            flash('Relationship successfully edited.')
            return redirect(url_for('admin.admin'))

    return render_template('admin/define.html', title='Relationship Manager', form=form)
