from flask import render_template
from flask_login import login_required
from main.models import Opportunity
from flask_table import Table, Col
from main.opp import opp_bp


@opp_bp.route('/opportunity')
@login_required
def opportunity():
    opp = Opportunity.query.all()

    # Declaration of the opportunity table to be presented in HTML form
    class OppTable(Table):
        classes = ['table', 'table-bordered', 'table-hover']

        CRM_Appln_No = Col('CRM_Appln_No')
        id = Col('id')

        Cust_Indicator = Col('Cust_Indicator')
        Fullname = Col('Fullname')
        ID_No = Col('ID_No')

        Created_by_name = Col('Created_by_name')
        Created_by_ID = Col('Created_by_ID')
        Create_date = Col('Create_date')

        Closed_by_name = Col('Closed_by_name')
        Closed_by_ID = Col('Closed_by_ID')
        Close_date = Col('Close_date')

        Assign_to_name = Col('Assign_to_name')
        Assign_to_ID = Col('Assign_to_ID')

        Insurance_Ref = Col('Insurance_Ref')

        Product_Name_L1 = Col('Product_Name_L1')
        Product_Name_L2 = Col('Product_Name_L2')
        Product_Name_L3 = Col('Product_Name_L3')
        Product_Code = Col('Product_Code')

        SalesType = Col('SalesType')
        RefNo_Caption = Col('RefNo_Caption')
        Base_Curr_Caption = Col('Base_Curr_Caption')
        Alt_Curr_Caption = Col('Alt_Curr_Caption')
        Opty_Amt_Caption = Col('Opty_Amt_Caption')
        Opty_Amt = Col('Opty_Amt')
        OD_Facility_Amt = Col('OD_Facility_Amt')

        Currency_code = Col('Currency_code')
        AltCurrency_code = Col('AltCurrency_code')

        Opty_Source = Col('Opty_Source')
        Opty_Type = Col('Opty_Type')
        Referral_Code = Col('Referral_Code')
        Referral_Comment = Col('Referral_Comment')

        Match = Col('Match')
        Acct_No = Col('Acct_No')
        Acct_open_date = Col('Acct_open_date')
        Match_Amt = Col('Match_Amt')

        Decline = Col('Decline')
        Decline_by_ID = Col('Decline_by_ID')
        Decline_by_name = Col('Decline_by_name')
        Decline_date = Col('Decline_date')
        Decline_Reason = Col('Decline_Reason')

        Assign_by_ID = Col('Assign_by_ID')
        Assign_by_dt = Col('Assign_by_dt')

        rp_pymt_freq = Col('rp_pymt_freq')
        FD_TENOR = Col('FD_TENOR')
        WEIGHTED_MARGIN = Col('WEIGHTED_MARGIN')
        PRE_RECEIVE = Col('PRE_RECEIVE')
        INTERIM_REV_PTS = Col('INTERIM_REV_PTS')

        Admin_Update = Col('Admin_Update')
        Updated_by_name = Col('Updated_by_name')
        Updated_by_ID = Col('Updated_by_ID')
        Update_date = Col('Update_date')

        Match_Dt = Col('Match_Dt')
        Unmatch_Dt = Col('Unmatch_Dt')

        RevShareTSO = Col('RevShareTSO')
        RevShareRM = Col('RevShareRM')
        INTERIM_REV_PTS_TSO = Col('INTERIM_REV_PTS_TSO')
        RP_Term = Col('RP_Term')
        FNA_No = Col('FNA_No')

        Property_Status = Col('Property_Status')
        Property_Type = Col('Property_Type')

    opp_table = OppTable(opp)
    return render_template('opp/opportunity.html', title='Opportunity Database', opp_table=opp_table)
