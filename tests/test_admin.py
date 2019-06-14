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

    u1 = User(staff_id='0000001', staff_name='Test Banker', staff_designation='Banker', permission_lvl=0, team='Team A')
    a = User(staff_id='4000001', staff_name='Test Administrator', staff_designation='Account Manager', permission_lvl=4)
    for u in [u1, a]:
        u.set_password('testing')
        db.session.add(u)
    db.session.commit()

    yield db

    db.drop_all()


def login(client, staff_id, password):
    return client.post('/auth/login', data=dict(staff_id=staff_id, password=password), follow_redirects=True)


def logout(client):
    return client.get('/auth/logout', follow_redirects=True)


def test_add_edit_user(test_client, init_database):
    login(test_client, '4000001', 'testing')  # Log in as an admin

    # Should be able to add a new user
    response = test_client.post('/admin/edit', data=dict(staff_id='1000001',
                                                         staff_name='Test Team Lead',
                                                         staff_designation='Team Lead',
                                                         permission_lvl=1,
                                                         team='Team B'),
                                follow_redirects=True)
    assert b'User successfully added.' in response.data

    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'1000001' in response.data
    assert b'Test Team Lead' in response.data

    # Should not be able to add a new admin account
    response = test_client.post('/admin/edit', data=dict(staff_id='4000002',
                                                         staff_name='I am a new admin',
                                                         staff_designation='Account Manager',
                                                         permission_lvl=4,
                                                         team='Team A'),
                                follow_redirects=True)
    assert b'Not a valid choice' in response.data
    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'I am a new admin' not in response.data

    # Should be able to edit an existing user
    response = test_client.post('/admin/edit?staff_id=0000001', data=dict(staff_id='0000001',
                                                                          staff_name='Banker X',
                                                                          staff_designation='Banker',
                                                                          permission_lvl=0,
                                                                          team='Team X'),
                                follow_redirects=True)
    assert b'User successfully edited.' in response.data

    response = test_client.get('/admin/admin', follow_redirects=True)
    assert b'Banker X' in response.data
    assert b'Team X' in response.data
    assert b'Test Banker' not in response.data
    assert b'Team A' not in response.data

    # Trying to edit staff ID will be ignored
    response = test_client.post('/admin/edit?staff_id=0000001', data=dict(staff_id='0000002',
                                                                          staff_name='Banker X',
                                                                          staff_designation='Banker',
                                                                          permission_lvl=0,
                                                                          team='Team X'),
                                follow_redirects=True)
    assert b'0000001' in response.data
    assert b'0000002' not in response.data

    # Should not be able to edit an admin account
    response = test_client.post('/admin/edit?staff_id=4000001', data=dict(staff_id='4000001',
                                                                          staff_name='Demoted to a Banker',
                                                                          staff_designation='Banker',
                                                                          permission_lvl=0,
                                                                          team='Team A'),
                                follow_redirects=True)
    assert b'To prevent disaster, you cannot edit an Administrator account' in response.data
    assert b'Demoted to a Banker' not in response.data
    assert b'Test Administrator' in response.data

    # Newly created user should be able to log in
    logout(test_client)
    response = login(test_client, '1000001', 'test')  # Log in with the default password
    assert b'Welcome, Test Team Lead!' in response.data

    # Non-admin should not be able to add or edit users
    response = test_client.post('/admin/edit', data=dict(staff_id='2000001',
                                                         staff_name='Test Team Manager',
                                                         staff_designation='Team Manager',
                                                         permission_lvl=2,
                                                         team='Team C'),
                                follow_redirects=True)
    assert b'User successfully added.' not in response.data
    assert b'You have no permission to do this action.' in response.data

    response = test_client.post('/admin/edit?staff_id=0000001', data=dict(staff_id='0000001',
                                                                          staff_name='Try harder',
                                                                          staff_designation='Fake administrator',
                                                                          permission_lvl=0,
                                                                          team='Team Z'),
                                follow_redirects=True)
    assert b'User successfully edited.' not in response.data
    assert b'You have no permission to do this action.' in response.data


# TODO: Write test for deleting user
# TODO: Write test for resetting the user password
# TODO: Write test for adding relationship
# TODO: Write test for deleting relationship

