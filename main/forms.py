from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, RadioField
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


class ApproveForm(FlaskForm):
    req_id = StringField('Enter a valid Request ID to approve', validators=[DataRequired()])  # Must be within length
    submit = SubmitField('Approve')


class AccountManagerForm(FlaskForm):
    operation = SelectField('What would you like to do?', choices=[('add', 'Add a new user'),
                                                                   ('edit', 'Edit an existing user'),
                                                                   ('delete', 'Delete an existing user')],
                            validators=[DataRequired()])

    staff_id = StringField('Staff ID', validators=[DataRequired()])
    staff_name = StringField('Staff Name', validators=[DataRequired()])
    staff_designation = StringField('Staff Designation', validators=[DataRequired()])
    has_permission = SelectField('Permission Level', choices=[('1', '1'),
                                                              ('0', '0')],
                                 validators=[DataRequired()])

    submit = SubmitField('Submit')
