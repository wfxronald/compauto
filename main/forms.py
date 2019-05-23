from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MainForm(FlaskForm):
    # TO-DO: To be changed to use a drop-down list, which is less prone to error
    # TO-DO: Also can try to include a database consisting of name of staff and staff ID, to bind the data together
    # so that there is no need to retype Staff ID multiple times
    created_by_name = StringField('Name of Staff', validators=[DataRequired()])
    created_by_id = StringField('Staff ID', validators=[DataRequired()])
    create_date = DateField('Date Created in YYYY-MM-DD format', validators=[DataRequired()])

    closed_by_name = StringField('Name of Staff', validators=[DataRequired()])
    closed_by_id = StringField('Staff ID', validators=[DataRequired()])
    close_date = DateField('Date Closed in YYYY-MM-DD format', validators=[DataRequired()])

    assign_to_name = StringField('Name of Staff', validators=[DataRequired()])
    assign_to_id = StringField('Staff ID', validators=[DataRequired()])

    pdt_name = StringField('Product Name', validators=[DataRequired()])

    submit = SubmitField('Submit Form')
