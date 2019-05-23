from main import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from main import login


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
