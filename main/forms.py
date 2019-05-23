from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MockForm(FlaskForm):
    username = StringField('Name of Staff', validators=[DataRequired()])
    userid = StringField('Staff ID', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    date = DateField('Date Appealed (in "YYYY-MM-DD" format)', validators=[DataRequired()])
    submit = SubmitField('Submit Form')


class MainForm(FlaskForm):
    created_by_name = StringField('Name of Staff')
    created_by_id = StringField('Staff ID')
    create_date = DateField('Date Created')

    closed_by_name = StringField('Name of Staff')
    closed_by_id = StringField('Staff ID')
    close_date = DateField('Date Closed')

    assign_to_name = StringField('Name of Staff')
    assign_to_id = StringField('Staff ID')

    pdt_name = StringField('Product Name')
