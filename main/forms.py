from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MainForm(FlaskForm):
    crm_app_no = StringField('CRM Application Number', validators=[DataRequired()])

    reason = SelectField('Reason for Appeal', choices=[('late', 'Close late'),
                                                       ('forget', 'Forget to close'),
                                                       ('assign', 'Assign wrongly'),
                                                       ('decline', 'Decline opportunity'),
                                                       ('unlock', 'Unlock opportunity'),
                                                       ('other', 'Other issues: manual')],
                         validators=[DataRequired()])

    closed_by_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    closed_by_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])

    assign_to_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    assign_to_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])

    submit = SubmitField('Submit Form')


class AccountManagerForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    staff_designation = StringField('Staff Designation', validators=[DataRequired()])
    permission_lvl = SelectField('Permission Level', choices=[('0', '0: Banker'),
                                                              ('1', '1: Team Lead'),
                                                              ('2', '2: Sales Head')],
                                 validators=[DataRequired()])
    team = StringField('Team', validators=[DataRequired()])

    submit = SubmitField('Submit')


class RelationshipForm(FlaskForm):
    begin = StringField('Relationship begins from', validators=[DataRequired()])
    end = StringField('Relationship ends at', validators=[DataRequired()])
    table_to_add = SelectField('Add this relationship to', choices=[('Role', 'Role Table'),
                                                                    ('Team', 'Team Table')],
                               validators=[DataRequired()])

    submit = SubmitField('Add')
