from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MainForm(FlaskForm):
    closed_by_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    closed_by_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])
    close_date = DateField('Date Closed in YYYY-MM-DD format', validators=[DataRequired()])

    assign_to_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    assign_to_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])

    submit = SubmitField('Submit Form')


class ApproveForm(FlaskForm):
    req_id = StringField('Enter a valid Request ID to approve', validators=[DataRequired()])  # Must be within length
    submit = SubmitField('Approve')
