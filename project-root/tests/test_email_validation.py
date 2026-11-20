import pytest

from app.email_validation import is_valid_email


@pytest.mark.parametrize(
    "email",
    ["rita@example.com", "first.last+tag@sub.example.org"],
)
def test_is_valid_email_accepts_common_addresses(email):
    assert is_valid_email(email)


@pytest.mark.parametrize(
    "email",
    [
        "not-an-email",
        "name@localhost",
        "name..last@example.com",
        ".name@example.com",
        "name@example..com",
        "name @example.com",
    ],
)
def test_is_valid_email_rejects_malformed_addresses(email):
    assert not is_valid_email(email)
