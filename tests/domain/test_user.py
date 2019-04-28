"""Test a user model."""
import attr
import pytest  # type: ignore
from werkzeug.security import generate_password_hash  # type: ignore

from crib.domain import User


@pytest.fixture
def fred():
    return User(username="fred", password="passwd")


@pytest.fixture
def tank():
    pw = generate_password_hash("passwd")
    return User(username="fred", password=pw)


def test_user_attributes(fred):
    """Test User attributes."""

    assert fred.username == "fred"
    assert fred.password == "passwd"


def test_user_frozen(fred):
    """Test a user cannot be modifed."""
    with pytest.raises(attr.exceptions.FrozenInstanceError):
        fred.username = "derf"


def test_name_too_short():
    """Test that a name must have at least 3 characters."""
    with pytest.raises(ValueError):
        User(username="ab", password="passwd")


def test_pw_too_short():
    """Test that a password hash must have at least 3 characters."""
    with pytest.raises(ValueError):
        User(username="passwd", password="ab")


def test_valid_password(tank):
    """Test is a valid password is recognized."""
    assert tank.is_password_valid("passwd")


def test_invalid_password(tank):
    """Test is an invalid password is flagged."""
    assert not tank.is_password_valid("not the passwd")
