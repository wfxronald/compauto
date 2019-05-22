from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MockForm(FlaskForm):
    username = StringField('Name of Staff', validators=[DataRequired()])
    userid = StringField('Staff ID', validators=[DataRequired()])
    designation = StringField('Designation', validators=[DataRequired()])
    date = DateField('Date Appealed (in "YYYY-MM-DD" format)', validators=[DataRequired()])
    submit = SubmitField('Submit Form')
