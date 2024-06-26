import pytest
import requests
from api.post_sign_up import SignUp
from generators.user_generator import get_random_user


@pytest.fixture
def sign_up_api():
    return SignUp()


def test_successful_api_signup(sign_up_api: SignUp):
    user = get_random_user()
    response = sign_up_api.api_call(user)
    assert response.status_code == 201, "Expected status code 201"
    assert response.json().get("token") is not None, "Token should not be None"


def test_should_return_400_if_username_too_short(sign_up_api: SignUp):
    user = get_random_user()
    user.username = "abc"  # intentionally short username
    try:
        response = sign_up_api.api_call(user)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 400, "Expected status code 400"
        assert (
            "username length" in e.response.json()["username"]
        ), "Username error should mention length"


def test_should_return_400_if_password_too_short(sign_up_api: SignUp):
    user = get_random_user()
    user.password = "123"  # intentionally short password
    try:
        response = sign_up_api.api_call(user)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 400, "Expected status code 400"
        assert (
            "password length" in e.response.json()["password"]
        ), "Password error should mention length"


def test_should_return_400_if_email_invalid(sign_up_api: SignUp):
    user = get_random_user()
    user.email = "not-an-email"  # intentionally invalid email
    try:
        response = sign_up_api.api_call(user)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 400, "Expected status code 400"
        assert (
            "must be a well-formed email address" in e.response.json()["email"]
        ), "Email error should mention being a well-formed email address"


def test_should_return_400_if_missing_roles(sign_up_api: SignUp):
    user = get_random_user()
    user.roles = []  # intentionally missing roles
    try:
        response = sign_up_api.api_call(user)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 400, "Expected status code 400"
        assert "Please pick at least one role" in e.response.json()["roles"], "Roles error should mention requirement"


def test_should_return_400_if_invalid_role(sign_up_api: SignUp):
    user = get_random_user()
    user.roles = ["INVALID_ROLE"]  # intentionally invalid role
    try:
        response = sign_up_api.api_call(user)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 400, "Expected status code 400"
        assert "invalid role" in e.response.json()["roles"], "Roles error should mention invalid role"

def test_signup_existing_user_account(sign_up_api: SignUp):
    # First, sign up a new user
    new_user = get_random_user()
    response = sign_up_api.api_call(new_user)
    assert response.status_code == 201, "Expected status code 201"

    # Try to sign up the same user again
    try:
        second_response = sign_up_api.api_call(new_user)
        second_response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        assert e.response.status_code == 422, "Username is already in use"
        assert "Username is already in use" in e.response.json()["message"], "Expected error message for existing account"