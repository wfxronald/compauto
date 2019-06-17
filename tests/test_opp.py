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
              permission_lvl=1, team='Team B')
    u3 = User(staff_id='2000001', staff_name='Test Team Manager', staff_designation='Team Manager',
              permission_lvl=2, team='Team C')
    u4 = User(staff_id='3000001', staff_name='Test Sales Head', staff_designation='Sales Head',
              permission_lvl=3, team='Team D')

    v1 = User(staff_id='0000002', staff_name='Test Banker 2', staff_designation='Banker',
              permission_lvl=0, team='Team A2')
    for u in [u1, u2, u3, u4, v1]:
        u.set_password('testing')
        db.session.add(u)
    db.session.commit()

    opp = Opportunity(CRM_Appln_No='AD123456789', Match="N")
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


def test_modify_opportunity_late(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='late',  # Reason is close late
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'<td>Y</td>' in response.data  # A cell containing "Y" - match column
    logout(test_client)


def test_modify_opportunity_forget(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='forget',  # Reason is forget to close
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'<td>Y</td>' in response.data  # A cell containing "Y" - match column
    assert b'0000001' in response.data
    assert b'Test Banker' in response.data
    logout(test_client)


def test_modify_opportunity_assign(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='assign',  # Reason is assign wrongly
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'0000002' in response.data
    assert b'Test Banker 2' in response.data
    logout(test_client)


def test_modify_opportunity_decline(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='decline',  # Reason is decline opportunity
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'<td>Y</td>' in response.data  # A cell containing "Y" - decline column
    assert b'<td>N</td>' not in response.data  # No cell containing "N" - blanking out match column
    assert b'3000001' in response.data
    assert b'Test Sales Head' in response.data
    logout(test_client)


def test_modify_opportunity_unlock(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='unlock',  # Reason is unlock opportunity
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'<td>N</td>' not in response.data  # No cell containing "N" - blanking out match column
    logout(test_client)


def test_modify_opportunity_other(test_client, init_database):
    login(test_client, '0000001', 'testing')
    test_client.post('/index', data=dict(crm_app_no='AD123456789',
                                         reason='other',  # Reason is other issues: manual
                                         closed_by_name='Test Banker',
                                         closed_by_id='0000001',
                                         assign_to_name='Test Banker 2',
                                         assign_to_id='0000002'),
                     follow_redirects=True)
    logout(test_client)

    login(test_client, '1000001', 'testing')  # Approval by Team Lead
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '2000001', 'testing')  # Approval by Team Manager
    test_client.post('/dash/approve?id=1', follow_redirects=True)
    logout(test_client)

    login(test_client, '3000001', 'testing')  # Approval by Sales Head
    test_client.post('/dash/approve?id=1', follow_redirects=True)

    response = test_client.get('/opp/opportunity', follow_redirects=True)
    assert b'<td>N</td>' in response.data  # Nothing should have changed, match is still "N"
    logout(test_client)
