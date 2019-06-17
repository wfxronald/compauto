from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, ValidationError
from main.models import User, Team, Opportunity
from flask_login import current_user


class LoginForm(FlaskForm):
    staff_id = StringField('Staff ID', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


class MainForm(FlaskForm):
    crm_app_no = StringField('CRM Application Number', validators=[DataRequired()])

    def validate_crm_app_no(self, field):  # Foreign key check, if does not exist in the database then reject
        if not Opportunity.query.filter_by(CRM_Appln_No=field.data).first():
            raise ValidationError('The CRM Application Number you input does not exist in the database.')

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

    def validate_staff_id(self, field):
        if User.query.filter_by(staff_id=field.data).first():
            raise ValidationError('The staff ID has existed in the database! Choose another ID.')

    staff_name = StringField('Staff Name', validators=[DataRequired()])
    staff_designation = StringField('Staff Designation', validators=[DataRequired()])
    permission_lvl = SelectField('Permission Level', choices=[('0', '0: Banker'),
                                                              ('1', '1: Team Lead'),
                                                              ('2', '2: Team Manager'),
                                                              ('3', '3: Sales Head')],
                                 validators=[DataRequired()])
    team = StringField('Team', validators=[DataRequired()])

    submit = SubmitField('Submit')


class RelationshipForm(FlaskForm):
    begin = StringField('Relationship begins from', validators=[DataRequired()])
    end = StringField('Relationship ends at', validators=[DataRequired()])
    team_id = None

    def __init__(self, team_id=None, **kwargs):
        super().__init__(**kwargs)
        self.team_id = team_id

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        # If there is no change to the field, can simply ignore the validation and move on
        if self.team_id and Team.query.filter_by(id=self.team_id).first().from_team == self.begin.data \
                and Team.query.filter_by(id=self.team_id).first().to_team == self.end.data:
            return True

        if Team.query.filter_by(from_team=self.begin.data, to_team=self.end.data).first():
            self.begin.errors.append('Such relationship already exists in the database.')
            self.end.errors.append('Such relationship already exists in the database.')
            return False

        return True

    submit = SubmitField('Submit')


class ChangePasswordForm(FlaskForm):
    old_pass = PasswordField('Old Password', validators=[DataRequired()])
    new_pass = PasswordField('New Password', validators=[DataRequired()])
    repeat_new_pass = PasswordField('Repeat New Password', validators=[DataRequired()])

    def validate(self):
        if not FlaskForm.validate(self):
            return False

        if self.new_pass.data != self.repeat_new_pass.data or not current_user.check_password(self.old_pass.data):
            self.old_pass.errors.append('Old password is incorrect or new passwords do not match!')
            self.new_pass.errors.append('Old password is incorrect or new passwords do not match!')
            self.repeat_new_pass.errors.append('Old password is incorrect or new passwords do not match!')
            return False

        return True

    submit = SubmitField('Submit')
