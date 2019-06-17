import os
import sys
import pytest

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
              permission_lvl=1, team='Team A')
    u3 = User(staff_id='2000001', staff_name='Test Team Manager', staff_designation='Team Manager',
              permission_lvl=2, team='Team A')
    u4 = User(staff_id='3000001', staff_name='Test Sales Head', staff_designation='Sales Head',
              permission_lvl=3, team='Team A')
    u5 = User(staff_id='4000001', staff_name='Test Administrator', staff_designation='Account Manager',
              permission_lvl=4, team='Team A')
    for u in [u1, u2, u3, u4, u5]:
        u.set_password('testing')
        db.session.add(u)

    opp = Opportunity(CRM_Appln_No='AD123456789')
    req = Request(crm_app_no='AD123456789', reason='late', closed_by_name='Test Banker', closed_by_id='0000001',
                  assign_to_name='Test Banker', assign_to_id='0000001')
    db.session.add(opp)
    db.session.add(req)
    db.session.commit()

    yield db

    db.drop_all()


def login(client, staff_id, password):
    return client.post('/auth/login', data=dict(staff_id=staff_id, password=password), follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


def test_guest_view(test_client, init_database):
    response = test_client.get('/', follow_redirects=True)
    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' not in response.data
    assert b'Change Password' not in response.data
    assert b'Logout' not in response.data
    assert b'Help' in response.data
    assert b'Login' in response.data
    assert b'Dashboard' not in response.data
    assert b'Account Manager' not in response.data

    # Check the content of the login page
    assert b'Sign In' in response.data

    # Guest can access help page
    response = test_client.get('/docs/docs', follow_redirects=True)
    assert b'Documentation' in response.data


def test_banker_view(test_client, init_database):
    response = login(test_client, '0000001', 'testing')

    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' in response.data
    assert b'Change Password' in response.data
    assert b'Logout' in response.data
    assert b'Help' in response.data
    assert b'Login' not in response.data
    assert b'Dashboard' not in response.data
    assert b'Account Manager' not in response.data

    # Check the content of the homepage
    assert b'Welcome, Test Banker!' in response.data
    assert b'You cannot raise any sales opportunity appeal.' not in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'Do check that these details are correct. Otherwise, contact your administrator!' in response.data
    assert b'CRM Application Number Verifier' in response.data
    assert b'Sales Opportunity Appeal Form' in response.data

    # Try accessing admin page
    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'You have no permission to access this page.' in response.data

    # Try accessing dashboard
    response = test_client.get('/dash/dashboard', follow_redirects=True)
    assert b'You have no permission to access this page.' in response.data

    logout(test_client)


def test_team_lead_view(test_client, init_database):
    response = login(test_client, '1000001', 'testing')

    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' in response.data
    assert b'Change Password' in response.data
    assert b'Logout' in response.data
    assert b'Help' in response.data
    assert b'Login' not in response.data
    assert b'Dashboard' in response.data
    assert b'Account Manager' not in response.data

    # Check the content of the homepage
    assert b'Welcome, Test Team Lead!' in response.data
    assert b'You cannot raise any sales opportunity appeal.' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'Do check that these details are correct. Otherwise, contact your administrator!' in response.data
    assert b'CRM Application Number Verifier' not in response.data
    assert b'Sales Opportunity Appeal Form' not in response.data

    # Try accessing admin page
    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'You have no permission to access this page.' in response.data

    logout(test_client)


def test_team_manager_view(test_client, init_database):
    response = login(test_client, '2000001', 'testing')

    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' in response.data
    assert b'Change Password' in response.data
    assert b'Logout' in response.data
    assert b'Help' in response.data
    assert b'Login' not in response.data
    assert b'Dashboard' in response.data
    assert b'Account Manager' not in response.data

    # Check the content of the homepage
    assert b'Welcome, Test Team Manager!' in response.data
    assert b'You cannot raise any sales opportunity appeal.' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'Do check that these details are correct. Otherwise, contact your administrator!' in response.data
    assert b'CRM Application Number Verifier' not in response.data
    assert b'Sales Opportunity Appeal Form' not in response.data

    # Try accessing admin page
    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'You have no permission to access this page.' in response.data

    logout(test_client)


def test_sales_head_view(test_client, init_database):
    response = login(test_client, '3000001', 'testing')

    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' in response.data
    assert b'Change Password' in response.data
    assert b'Logout' in response.data
    assert b'Help' in response.data
    assert b'Login' not in response.data
    assert b'Dashboard' in response.data
    assert b'Account Manager' not in response.data

    # Check the content of the homepage
    assert b'Welcome, Test Sales Head!' in response.data
    assert b'You cannot raise any sales opportunity appeal.' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'Do check that these details are correct. Otherwise, contact your administrator!' in response.data
    assert b'CRM Application Number Verifier' not in response.data
    assert b'Sales Opportunity Appeal Form' not in response.data

    # Try accessing admin page
    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'You have no permission to access this page.' in response.data

    logout(test_client)


def test_admin_view(test_client, init_database):
    response = login(test_client, '4000001', 'testing')

    # Check the navbar view
    assert b'Home' in response.data
    assert b'Opportunity Database' in response.data
    assert b'Change Password' in response.data
    assert b'Logout' in response.data
    assert b'Help' in response.data
    assert b'Login' not in response.data
    assert b'Dashboard' in response.data
    assert b'Account Manager' in response.data

    # Check the content of the homepage
    assert b'Welcome, Test Administrator!' in response.data
    assert b'You cannot raise any sales opportunity appeal.' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'The details here should be correct.' in response.data
    assert b'CRM Application Number Verifier' not in response.data
    assert b'Sales Opportunity Appeal Form' not in response.data

    # Try approving request -> rejected
    response = test_client.post('/dash/approve?id=1', follow_redirects=True)
    assert b'You are not allowed to approve any appeal. Proceed to Account Manager to manage accounts instead.' \
           in response.data

    logout(test_client)
