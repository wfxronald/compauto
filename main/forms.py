from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, RadioField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MainForm(FlaskForm):
    reason = RadioField('Reason for Request', choices=[('closed', 'Close-related issues: Closed late, forgot to close'),
                                                       ('assigned', 'Assign-related issues: Assigned wrongly'),
                                                       ('others', 'Other issues: Keyed in wrongly, etc')],
                        validators=[DataRequired()])

    created_by_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    created_by_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])
    create_date = DateField('Date Created in YYYY-MM-DD format', validators=[DataRequired()])

    closed_by_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    closed_by_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])
    close_date = DateField('Date Closed in YYYY-MM-DD format', validators=[DataRequired()])

    assign_to_name = SelectField('Name of Staff', coerce=str, validators=[DataRequired()])
    assign_to_id = SelectField('Staff ID', coerce=str, validators=[DataRequired()])

    pdt_name = StringField('Product Name', validators=[DataRequired()])

    submit = SubmitField('Submit Form')
