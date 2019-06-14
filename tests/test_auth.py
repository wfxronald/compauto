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


@pytest.fixture(scope='module')
def test_client():
    flask_app = create_app(TestConfig)
    testing_client = flask_app.test_client()

    ctx = flask_app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    u1 = User(staff_id='0000001', staff_name='Test User', staff_designation='Banker', permission_lvl=0, team='Team A')
    u1.set_password('testing')
    db.session.add(u1)
    db.session.commit()

    yield db

    db.drop_all()


def test_homepage(test_client):
    response = test_client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'Please log in to access this page.' in response.data


def login(client, staff_id, password):
    return client.post('/auth/login', data=dict(staff_id=staff_id, password=password), follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


def test_login_and_logout(test_client, init_database):
    # Valid staff id with wrong password
    response = login(test_client, '0000001', 'wrong_password')
    assert b'Invalid staff ID or password.' in response.data

    # Invalid staff id with password found in the database
    response = login(test_client, '9999999', 'testing')
    assert b'Invalid staff ID or password.' in response.data

    # Valid staff id with correct password -> logged in
    response = login(test_client, '0000001', 'testing')
    assert b'Welcome, Test User!' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'CRM Application Number Verifier' in response.data
    assert b'Sales Opportunity Appeal Form' in response.data

    # Already logged in, tries to log in again -> returns to home
    response = login(test_client, '9999999', 'whatever')
    assert b'Welcome, Test User!' in response.data
    assert b'Automatically Generated Details' in response.data
    assert b'CRM Application Number Verifier' in response.data
    assert b'Sales Opportunity Appeal Form' in response.data

    # Signed in and tries to log out -> logged out
    response = logout(test_client)
    assert b'You have been logged out.' in response.data


def change_pass(client, old_pass, new_pass, repeat_new_pass):
    return client.post('/auth/change', data=dict(old_pass=old_pass,
                                                 new_pass=new_pass,
                                                 repeat_new_pass=repeat_new_pass),
                       follow_redirects=True)


def test_change_password(test_client, init_database):
    ####################################################################
    # Test 1 - Incorrectly input old password -> password is unchanged #
    ####################################################################
    login(test_client, '0000001', 'testing')
    response = change_pass(test_client, 'wrong_pass', 'new_pass', 'new_pass')
    assert b'Old password is incorrect or new passwords do not match!' in response.data
    logout(test_client)
    response = login(test_client, '0000001', 'new_pass')
    assert b'Invalid staff ID or password.' in response.data  # Password is unchanged

    ##########################################################################
    # Test 2 - Incorrectly repeats the new password -> password is unchanged #
    ##########################################################################
    login(test_client, '0000001', 'testing')
    response = change_pass(test_client, 'testing', 'new_pass', 'oops_pass')
    assert b'Old password is incorrect or new passwords do not match!' in response.data
    logout(test_client)
    response = login(test_client, '0000001', 'new_pass')
    assert b'Invalid staff ID or password.' in response.data  # Password is unchanged

    ##############################################
    # Test 3 - Successfully changed the password #
    ##############################################
    login(test_client, '0000001', 'testing')
    response = change_pass(test_client, 'testing', 'new_pass', 'new_pass')
    assert b'Password successfully changed.' in response.data
    logout(test_client)
    response = login(test_client, '0000001', 'testing')
    assert b'Invalid staff ID or password.' in response.data  # Password has been changed, cannot use old password
    response = login(test_client, '0000001', 'new_pass')
    assert b'Welcome, Test User!' in response.data  # Successfully logged in
    assert b'Automatically Generated Details' in response.data
    assert b'CRM Application Number Verifier' in response.data
    assert b'Sales Opportunity Appeal Form' in response.data
