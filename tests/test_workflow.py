import os
import sys
import pytest
from flask import json

# Include the path of the root directory
path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, path + '/../')
from main import create_app
from main.models import *


class TestConfig(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    TESTING = True
    WTF_CSRF_ENABLED = False  # Should only be done during testing


@pytest.fixture(scope='class')
def test_client():
    flask_app = create_app(TestConfig)
    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='class')
def init_database():
    db.create_all()

    u1 = User(staff_id='0000001', staff_name='Test Banker', staff_designation='Banker',
              permission_lvl=0, team='Team A')
    u2 = User(staff_id='1000001', staff_name='Test Team Lead', staff_designation='Team Lead',
              permission_lvl=1, team='Team B')
    u3 = User(staff_id='2000001', staff_name='Test Team Manager', staff_designation='Team Manager',
              permission_lvl=2, team='Team C')
    u4 = User(staff_id='3000001', staff_name='Test Sales Head', staff_designation='Sales Head',
              permission_lvl=3, team='Team D')
    u5 = User(staff_id='4000001', staff_name='Test Administrator', staff_designation='Account Manager', permission_lvl=4)

    v1 = User(staff_id='0000002', staff_name='Test Banker 2', staff_designation='Banker',
              permission_lvl=0, team='Team A2')
    v2 = User(staff_id='1000002', staff_name='Test Team Lead 2', staff_designation='Team Lead',
              permission_lvl=1, team='Team B2')
    v3 = User(staff_id='2000002', staff_name='Test Team Manager 2', staff_designation='Team Manager',
              permission_lvl=2, team='Team C2')
    v4 = User(staff_id='3000002', staff_name='Test Sales Head 2', staff_designation='Sales Head',
              permission_lvl=3, team='Team D2')
    for u in [u1, u2, u3, u4, u5, v1, v2, v3, v4]:
        u.set_password('testing')
        db.session.add(u)
    db.session.commit()

    opp = Opportunity(CRM_Appln_No='AD123456789')
    db.session.add(opp)
    db.session.commit()

    # Define the workflow as Team A -> Team B -> Team C -> Team D
    r1 = Team(from_team='Team A', to_team='Team B')
    r2 = Team(from_team='Team B', to_team='Team C')
    r3 = Team(from_team='Team C', to_team='Team D')
    for r in [r1, r2, r3]:
        db.session.add(r)
    db.session.commit()

    yield db

    db.drop_all()


def login(client, staff_id, password):
    return client.post('/auth/login', data=dict(staff_id=staff_id, password=password), follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


def test_crm_no_verifier(test_client, init_database):
    response = test_client.post('/receiver', data=json.dumps(dict(crm_app_no="AD123456789")),
                                content_type='application/json', follow_redirects=True)
    assert b'"success":true' in response.data

    # Put in a random crm_app_no that does not exist -> fails
    response = test_client.post('/receiver', data=json.dumps(dict(crm_app_no="AD000000000")),
                                content_type='application/json', follow_redirects=True)
    assert b'"success":false' in response.data


def test_create_request(test_client, init_database):
    login(test_client, '0000001', 'testing')  # Login as a banker

    # No such CRM application number -> fails to create a request
    response = test_client.post('/index', data=dict(crm_app_no='AD000000000',
                                                    reason='late',
                                                    closed_by_name='Test Banker',
                                                    closed_by_id='0000001',
                                                    assign_to_name='Test Banker',
                                                    assign_to_id='0000001'),
                                follow_redirects=True)
    assert b'The CRM Application Number you input does not exist in the database.' in response.data
    assert b'Congratulations, your request has been stored in the database.' not in response.data

    # Should not be accessible from the dashboard
    logout(test_client)
    login(test_client, '1000001', 'testing')  # Login as a team lead
    response = test_client.get('/dash/dashboard', follow_redirects=True)
    assert b'AD000000000' not in response.data
    assert b'late' not in response.data
    assert b'No Items' in response.data

    # Cannot create a request as a team lead
    response = test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                                    reason='late',
                                                    closed_by_name='Test Team Lead',
                                                    closed_by_id='1000001',
                                                    assign_to_name='Test Team Lead',
                                                    assign_to_id='1000001'),
                                follow_redirects=True)
    assert b'Congratulations, your request has been stored in the database.' not in response.data
    assert b'You cannot raise any sales opportunity appeal.' in response.data

    # Successfully created -> stored in the database
    logout(test_client)
    login(test_client, '0000001', 'testing')  # Login as a banker
    response = test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                                    reason='late',
                                                    closed_by_name='Test Banker',
                                                    closed_by_id='0000001',
                                                    assign_to_name='Test Banker',
                                                    assign_to_id='0000001'),
                                follow_redirects=True)
    assert b'Congratulations, your request has been stored in the database.' in response.data

    # Stored in the database means that it should be accessible from the dashboard
    logout(test_client)
    login(test_client, '1000001', 'testing')  # Login as a team lead
    response = test_client.get('/dash/dashboard', follow_redirects=True)
    assert b'AD123456789' in response.data
    assert b'late' in response.data
    assert b'No Items' not in response.data

    logout(test_client)


def test_hierarchy_system(test_client, init_database):
    ###########################################
    # Step 1: Creation of a request by Banker #
    ###########################################
    # Use the request previously created by Test Banker, who is in Team A
    login(test_client, '0000001', 'testing')  # Login as a banker
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                                    reason='late',
                                                    closed_by_name='Test Banker',
                                                    closed_by_id='0000001',
                                                    assign_to_name='Test Banker',
                                                    assign_to_id='0000001'),
                     follow_redirects=True)
    logout(test_client)

    #################################
    # Step 2: Approval by Team Lead #
    #################################
    # Should not be able to approve request from Test Banker if not from Team B
    login(test_client, '1000002', 'testing')  # Login as Test Team Lead 2
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' in \
           response.data
    assert b'You have approved this appeal. Appeal is now pending for Team Manager approval.' not in response.data
    assert b'table-danger' not in response.data
    logout(test_client)

    # Team Manager and Sales Head cannot approve before Team Lead approves!
    login(test_client, '2000001', 'testing')  # Login as Test Team Manager
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'The request has not been approved by a Team Lead. Please wait for Team Lead&#39;s approval.' in \
           response.data
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Login as Test Sales Head
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'The request has not been approved by a Team Lead. Please wait for Team Lead&#39;s approval.' in \
           response.data
    logout(test_client)

    # Re-login as Test Team Lead, who is from Team B -> Should be able to approve
    login(test_client, '1000001', 'testing')  # Login as Test Team Lead
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' \
           not in response.data
    assert b'You have approved this appeal. Appeal is now pending for Team Manager approval.' in response.data
    assert b'table-danger' in response.data

    response = test_client.post('/dash/approve?id=1', follow_redirects=True)  # Cannot approve twice
    assert b'The request has been approved by Team Lead previously.' in response.data

    logout(test_client)

    ####################################
    # Step 3: Approval by Team Manager #
    ####################################
    # Should not be able to approve request after Test Team Lead (Team B) if not from Team C
    login(test_client, '2000002', 'testing')  # Login as Test Team Manager 2
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' in \
           response.data
    assert b'You have approved this appeal. Appeal is now pending for Sales Head approval.' not in response.data
    assert b'table-warning' not in response.data
    logout(test_client)

    # Sales Head cannot approve before Team Manager approves!
    login(test_client, '3000001', 'testing')  # Login as Test Sales Head
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'The request has not been approved by a Team Manager. Please wait for Team Manager&#39;s approval.' in \
           response.data
    logout(test_client)

    # Re-login as Test Team Manager, who is from Team C -> Should be able to approve
    login(test_client, '2000001', 'testing')  # Login as Test Team Manager
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' \
           not in response.data
    assert b'You have approved this appeal. Appeal is now pending for Sales Head approval.' in response.data
    assert b'table-warning' in response.data

    response = test_client.post('/dash/approve?id=1', follow_redirects=True)  # Cannot approve twice
    assert b'The request has been approved by Team Manager previously.' in response.data

    logout(test_client)

    ##################################
    # Step 4: Approval by Sales Head #
    ##################################
    # Should not be able to approve request after Test Team Manager (Team C) if not from Team D
    login(test_client, '3000002', 'testing')  # Login as Test Sales Head 2
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' in \
           response.data
    assert b'You have approved this appeal. Opportunity database has been modified.' not in response.data
    assert b'table-success' not in response.data
    logout(test_client)

    # Re-login as Test Sales Head, who is from Team D -> Should be able to approve
    login(test_client, '3000001', 'testing')  # Login as Test Sales Head
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not authorised to approve this request. Check again if you are approving the right request!' \
           not in response.data
    assert b'You have approved this appeal. Opportunity database has been modified.' in response.data
    assert b'table-success' in response.data

    response = test_client.post('/dash/approve?id=1', follow_redirects=True)  # Cannot approve twice
    assert b'The request has been approved before. Cannot approve a request twice!' in response.data

    logout(test_client)


def test_forget_set_team(test_client, init_database):
    # Create a mock request by Test Banker
    login(test_client, '0000001', 'testing')  # Login as a banker
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='late',
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker',
                                         assign_to_id='0000001'),
                     follow_redirects=True)
    logout(test_client)

    # Remove Test Team Lead's team
    User.query.filter_by(staff_id='1000001').first().team = ""

    # Now, Test Team Lead cannot approve even though Test Banker is in his team
    login(test_client, '1000001', 'testing')  # Login as Test Team Lead
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'An error has occurred on the administrator side. Please contact the administrator!' in response.data

    logout(test_client)


def test_forget_set_relationship(test_client, init_database):
    # Create a mock request by Test Banker
    login(test_client, '0000001', 'testing')  # Login as a banker
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='late',
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker',
                                         assign_to_id='0000001'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '4000001', 'testing')  # Log in as an admin
    test_client.post('/admin/clear?id=1', follow_redirects=True)  # 'Accidentally' delete some relationships
    test_client.post('/admin/clear?id=2', follow_redirects=True)
    test_client.post('/admin/clear?id=3', follow_redirects=True)
    logout(test_client)

    # Now, even if the workflow is correct, no one can approve anything
    login(test_client, '1000001', 'testing')  # Login as Test Team Lead
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'An error has occurred on the administrator side. Please contact the administrator!' in response.data
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Login as Test Team Manager
    # Pretend it has been approved by team lead
    r = Request.query.filter_by(id=1).first()
    r.is_approved_by_teamlead = True
    r.approving_teamlead_name = 'Test Team Lead'
    r.approving_teamlead_id = '1000001'
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'An error has occurred on the administrator side. Please contact the administrator!' in response.data
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Login as Test Sales Head
    # Pretend it has been approved by team manager
    r = Request.query.filter_by(id=1).first()
    r.is_approved_by_teammanager = True
    r.approving_teammanager_name = 'Test Team Manager'
    r.approving_teammanager_id = '2000001'
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'An error has occurred on the administrator side. Please contact the administrator!' in response.data
    logout(test_client)
