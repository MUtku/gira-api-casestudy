# -*- encoding: utf-8 -*-

"""
Copyright (c) 2019 - present AppSeed.us
"""

import pytest
import json

from api import app

"""
   Sample test data
"""

DUMMY_USERNAME = "apple"
DUMMY_EMAIL = "apple@apple.com"
DUMMY_PASS = "newpassword" 

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

@pytest.fixture()
def auth_token(client):
    '''
        Generate user token to use API
    '''
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    yield data["token"]

@pytest.fixture()
def auth_token_new(client):
    '''
        Generate user token to use API
    '''
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL + '_1',
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    yield data["token"]

@pytest.fixture()
def auth_token_new_1(client):
    '''
        Generate user token to use API
    '''
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL + '_2',
                "password": DUMMY_PASS + '_2'
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    yield data["token"]

'''
    Tests For Users Endpoint
'''
def test_user_signup(client):
    """
    Tests /users/register API
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "The user was successfully registered" in data["msg"]

def test_user_signup_invalid_data(client):
    """
    Tests /users/register API: invalid data like email field empty
    """
    response = client.post(
        "api/users/register",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME,
                "email": "",
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "'' is too short" in data["msg"]


def test_user_login_correct(client):
    """
    Tests /users/signup API: Correct credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_PASS
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert data["token"] != ""

def test_user_login_error(client):
    """
    Tests /users/signup API: Wrong credentials
    """
    response = client.post(
        "api/users/login",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL,
                "password": DUMMY_EMAIL
            }
        ),
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Wrong credentials." in data["msg"]

def test_user_edit_username_correct_input(client,auth_token):
    """
    Tests /users/signup API: Correct username
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME + '_1',
            },
        ),
        headers={"authorization":auth_token},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Successfully updated username" in data["msg"]

def test_user_edit_username_existing_username(client, auth_token):
    """
    Tests /users/edit API: existing username
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME + '_1',
            },
        ),
        headers={"authorization":auth_token},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Username already taken" in data["msg"]

def test_user_edit_email_correct_input(client, auth_token):
    """
    Tests /users/edit API: Correct email
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL + '_1',
            },
        ),
        headers={"authorization":auth_token},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Successfully updated email " in data["msg"]

def test_user_edit_email_existing_email(client, auth_token_new):
    """
    Tests /users/edit API: existing email
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "email": DUMMY_EMAIL + '_1',
            },
        ),
        headers={"authorization":auth_token_new},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 400
    assert "Email already taken" in data["msg"]

def test_user_edit_all_correct_input(client, auth_token_new):
    """
    Tests /users/edit API: Correct inputs
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "username": DUMMY_USERNAME + '_2',
                "email": DUMMY_EMAIL + '_2',
                "password": DUMMY_PASS + '_2'
            },
        ),
        headers={"authorization":auth_token_new},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Successfully updated username email password " in data["msg"]

def test_user_edit_password_correct_input(client, auth_token_new_1):
    """
    Tests /users/edit API: Correct password format
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {
                "password": DUMMY_PASS + '_2',
            },
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Successfully updated password " in data["msg"]

def test_user_edit_password_no_input(client, auth_token_new_1):
    """
    Tests /users/edit API: No input for editing
    """
    response = client.post(
        "api/users/edit",
        data=json.dumps(
            {},
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Nothing to update" in data["msg"]

def test_user_logout(client, auth_token_new_1):
    """
    Tests /users/edit API: Correct password format
    """
    response = client.post(
        "api/users/logout",
        data=json.dumps(
            {},
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert response.status_code == 200
    assert "Successfully logged out the user" in data["msg"]

'''
    Tests For Project Endpoint
'''
def test_project_create(client, auth_token_new_1):
    """
    Tests /project/create API using valid data
    """
    response = client.post(
        "api/project/create",
        data=json.dumps(
            {
                "project_name": "test_proj_1"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "Project successfully created" in data["msg"]
    assert response.status_code == 200

def test_project_create_existing_name(client, auth_token_new_1):
    """
    Tests /project/create API using vexisting project name
    """
    response = client.post(
        "api/project/create",
        data=json.dumps(
            {
                "project_name": "test_proj_1"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "A project with the same name already exists" in data["msg"]
    assert response.status_code == 400

def test_project_list_all_projects(client, auth_token_new_1):
    """
    Tests /project/listall API using valid data
    """
    response = client.get(
        "api/project/listall",
        data=json.dumps(
            {}
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "Projects of the current user successfully listed" in data["msg"]
    assert response.status_code == 200

def test_project_view_project(client, auth_token_new_1):
    """
    Tests /project/view API using valid data
    """
    response = client.get(
        "api/project/view",
        data=json.dumps(
            {
                "projectID":"1"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "Project content returned successfully" in data["msg"]
    assert response.status_code == 200

def test_project_view_project_not_in_scope(client, auth_token_new_1):
    """
    Tests /project/view API using a prroject id out of user scope
    """
    response = client.get(
        "api/project/view",
        data=json.dumps(
            {
                "projectID":"3"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "No such project found in the scope of this user" in data["msg"]
    assert response.status_code == 404

def test_project_edit_valid_project_valid_name(client, auth_token_new_1):
    """
    Tests /project/edit API using valid data
    """
    response = client.post(
        "api/project/edit",
        data=json.dumps(
            {
                "projectID":"1",
                "project_name":"new_proj_name"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "Project successfully edited" in data["msg"]
    assert response.status_code == 200

def test_project_edit_valid_project_existing_name(client, auth_token_new_1):
    """
    Tests /project/edit API using existing project name
    """
    response = client.post(
        "api/project/edit",
        data=json.dumps(
            {
                "projectID":"1",
                "project_name":"new_proj_name"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "A project with the same name already exists" in data["msg"]
    assert response.status_code == 400

def test_project_edit_out_of_scope_project_valid_name(client, auth_token_new_1):
    """
    Tests /project/edit API using out of scope project id
    """
    response = client.post(
        "api/project/edit",
        data=json.dumps(
            {
                "projectID":"3",
                "project_name":"test_proj_12"
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "No such project exists in the scope of the user" in data["msg"]
    assert response.status_code == 404

def test_project_delete_valid_project(client, auth_token_new_1):
    """
    Tests /project/delete API using project id
    """
    response = client.delete(
        "api/project/delete",
        data=json.dumps(
            {
                "projectID":"1",
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "Project and related issues deleted successfully" in data["msg"]
    assert response.status_code == 200

def test_project_delete_out_of_scope_project(client, auth_token_new_1):
    """
    Tests /project/delete API using out of scope project id
    """
    response = client.delete(
        "api/project/delete",
        data=json.dumps(
            {
                "projectID":"3",
            }
        ),
        headers={"authorization":auth_token_new_1},
        content_type="application/json")

    data = json.loads(response.data.decode())
    assert "No such project exists in the scope of the user" in data["msg"]
    assert response.status_code == 404