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
    Tests For User Endpoint
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

