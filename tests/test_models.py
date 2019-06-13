import os
import sys
from flask import Flask
import pytest
from werkzeug.urls import url_parse

# # Include the path of the root directory
# path = os.path.dirname(os.path.abspath(__file__))
# sys.path.insert(0, path + '/../')
# from main import app
# from main.models import *


@pytest.fixture(scope='module')
def test_client():
    app = Flask(__name__, instance_relative_config=True)
    app.config['BCRYPT_LOG_ROUNDS'] = 4  # To reduce the time taken for testing
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False  # Should only be done during testing
    db = SQLAlchemy(app)

    testing_client = app.test_client()
    ctx = app.app_context()
    ctx.push()

    yield testing_client

    ctx.pop()


@pytest.fixture(scope='module')
def init_database():
    db.create_all()

    u1 = User(staff_id='0000001', staff_name='Test User', staff_designation='Banker', permission_lvl=0, team='Team A')
    u2 = User(staff_id='0000002', staff_name='Test User 2', staff_designation='Banker', permission_lvl=0, team='Team B')
    u1.set_password('testing')
    u2.set_password('testing2')
    db.session.add(u1)
    db.session.add(u2)

    db.session.commit()

    yield db

    db.drop_all()


def test_homepage(test_client):
    """
    Asserts that user is not supposed to access the homepage when not logged in.
    :param test_client: An instance of the Flask app
    :return: Redirects user to login page
    """
    response = test_client.get('/')
    assert response.status_code == 302
    assert url_parse(response.location).path == '/login'


def test_login(test_client, init_database):
    response = test_client.post('/login', data=dict(staff_id='0000001', password='wrong_password'))
    assert response.status_code == 302
    assert url_parse(response.location).path == '/login'

    # def test_new_user(new_user):
    #     assert new_user.get_id() == '1234567'
    #     assert new_user.staff_name == 'Test User'
    #     assert new_user.staff_designation == 'Banker'
    #     assert new_user.permission_lvl == 0
    #     assert new_user.team == 'Team A'
    #     assert new_user.check_password('testing')
    #
    # @pytest.fixture(scope='module')
    # def new_request():
    #     req = Request(requester_name='Test User',
    #                   requester_id='1234567',
    #                   requester_designation=current_user.staff_designation,
    #                   request_date=current_time,
    #
    #                   crm_app_no=form.crm_app_no.data,
    #                   reason=form.reason.data,
    #
    #                   closed_by_name=form.closed_by_name.data,
    #                   closed_by_id=form.closed_by_id.data,
    #
    #                   assign_to_name=form.assign_to_name.data,
    #                   assign_to_id=form.assign_to_id.data,
    #
    #                   is_approved_by_teamlead=False,
    #                   is_approved_by_teammanager=False,
    #                   is_approved_by_saleshead=False)
    #
    #     user.set_password('testing')
    #     return user

