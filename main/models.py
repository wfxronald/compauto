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
    permission_lvl = db.Column(db.Integer)  # 0: Banker, 1: Team Lead, 2: Sales Head, 3: Account Manager
    parent_node = db.Column(db.String(10))  # Store the ID of the parent node, i.e. Banker -> Team Lead -> Sales Head

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

    crm_app_no = db.Column(db.String(15))
    reason = db.Column(db.String(10))  # Options: 'late', 'forget', 'assign', 'decline', 'unlock', 'other'

    closed_by_name = db.Column(db.String(120))
    closed_by_id = db.Column(db.String(10))

    assign_to_name = db.Column(db.String(120))
    assign_to_id = db.Column(db.String(10))

    # Storing the approval details of this request
    # Two-layered approval: team lead, then sales head
    is_approved_by_teamlead = db.Column(db.Boolean)
    approving_teamlead_name = db.Column(db.String(120))
    approving_teamlead_id = db.Column(db.String(120))
    teamlead_approve_date = db.Column(db.DateTime)

    is_approved_by_saleshead = db.Column(db.Boolean)
    approving_saleshead_name = db.Column(db.String(120))
    approving_saleshead_id = db.Column(db.String(120))
    saleshead_approve_date = db.Column(db.DateTime)

    def __repr__(self):
        return '<Request #{}>'.format(self.id)


class Opportunity(db.Model):
    CRM_Appln_No = db.Column(db.String(15), primary_key=True, index=True)  # A unique identifier of all opportunity
    id = db.Column(db.String(10))

    Cust_Indicator = db.Column(db.String(1))
    Fullname = db.Column(db.String(120))
    ID_No = db.Column(db.String(30))

    Created_by_name = db.Column(db.String(120))
    Created_by_ID = db.Column(db.String(10))
    Create_date = db.Column(db.DateTime)

    Closed_by_name = db.Column(db.String(120))
    Closed_by_ID = db.Column(db.String(10))
    Close_date = db.Column(db.DateTime)

    Assign_to_name = db.Column(db.String(120))
    Assign_to_ID = db.Column(db.String(10))

    Insurance_Ref = db.Column(db.String(10))

    Product_Name_L1 = db.Column(db.String(30))
    Product_Name_L2 = db.Column(db.String(30))
    Product_Name_L3 = db.Column(db.String(30))
    Product_Code = db.Column(db.String(30))

    SalesType = db.Column(db.String(30))
    RefNo_Caption = db.Column(db.String(30))
    Base_Curr_Caption = db.Column(db.String(60))
    Alt_Curr_Caption = db.Column(db.String(60))
    Opty_Amt_Caption = db.Column(db.String(60))
    Opty_Amt = db.Column(db.Float)
    OD_Facility_Amt = db.Column(db.Float)

    Currency_code = db.Column(db.String(5))
    AltCurrency_code = db.Column(db.String(5))

    Opty_Source = db.Column(db.String(120))
    Opty_Type = db.Column(db.String(120))
    Referral_Code = db.Column(db.String(10))
    Referral_Comment = db.Column(db.String(60))

    Match = db.Column(db.String(1))
    Acct_No = db.Column(db.String(10))
    Acct_open_date = db.Column(db.Date)
    Match_Amt = db.Column(db.Float)

    Decline = db.Column(db.String(1))
    Decline_by_ID = db.Column(db.String(10))
    Decline_by_name = db.Column(db.String(120))
    Decline_date = db.Column(db.DateTime)
    Decline_Reason = db.Column(db.String(120))

    Assign_by_ID = db.Column(db.String(10))
    Assign_by_dt = db.Column(db.DateTime)

    rp_pymt_freq = db.Column(db.String(30))
    FD_TENOR = db.Column(db.String(30))
    WEIGHTED_MARGIN = db.Column(db.Integer)
    PRE_RECEIVE = db.Column(db.Float)
    INTERIM_REV_PTS = db.Column(db.Float)

    Admin_Update = db.Column(db.String(60))
    Updated_by_name = db.Column(db.String(120))
    Updated_by_ID = db.Column(db.String(10))
    Update_date = db.Column(db.DateTime)

    Match_Dt = db.Column(db.DateTime)
    Unmatch_Dt = db.Column(db.DateTime)

    RevShareTSO = db.Column(db.Integer)
    RevShareRM = db.Column(db.Integer)
    INTERIM_REV_PTS_TSO = db.Column(db.Float)
    RP_Term = db.Column(db.String(30))
    FNA_No = db.Column(db.String(10))

    Property_Status = db.Column(db.String(60))
    Property_Type = db.Column(db.String(60))

    def __repr__(self):
        return '<Opportunity #{}>'.format(self.CRM_Appln_No)
