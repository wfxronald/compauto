from main import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from main import login
from datetime import datetime


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)  # This ID is a running number index
    staff_id = db.Column(db.String(10), index=True, unique=True)  # Staff ID will be the username
    staff_name = db.Column(db.String(120))
    password_hash = db.Column(db.String(128))

    # More details about the user
    staff_designation = db.Column(db.String(120))
    has_permission = db.Column(db.Boolean)

    def __repr__(self):
        return '<Staff {} with ID {}>'.format(self.staff_name, self.staff_id)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Request(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # This ID represents the unique identifier for each request

    requester_name = db.Column(db.String(120))
    requester_id = db.Column(db.String(10))
    requester_designation = db.Column(db.String(10))
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

    crm_app_no = db.Column(db.String(15))  # This should be a foreign key
    fna_no = db.Column(db.String(10))

    created_by_name = db.Column(db.String(120))
    created_by_id = db.Column(db.String(10))
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    closed_by_name = db.Column(db.String(120))
    closed_by_id = db.Column(db.String(10))
    close_date = db.Column(db.DateTime, default=datetime.utcnow)

    assign_to_name = db.Column(db.String(120))
    assign_to_id = db.Column(db.String(10))

    pdt_name = db.Column(db.String(60))

    def __repr__(self):
        return '<Request #{}>'.format(self.id)


class Opportunity(db.Model):
    crm_app_no = db.Column(db.String(15), primary_key=True)  # This is a unique identifier of all opportunity
    fna_no = db.Column(db.String(10))

    created_by_name = db.Column(db.String(120))
    created_by_id = db.Column(db.String(10))
    create_date = db.Column(db.DateTime, default=datetime.utcnow)

    closed_by_name = db.Column(db.String(120))
    closed_by_id = db.Column(db.String(10))
    close_date = db.Column(db.DateTime, default=datetime.utcnow)

    assign_to_name = db.Column(db.String(120))
    assign_to_id = db.Column(db.String(10))

    pdt_name = db.Column(db.String(60))

    def __repr__(self):
        return '<Opportunity #{}>'.format(self.crm_app_no)
