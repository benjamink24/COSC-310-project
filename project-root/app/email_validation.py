import re


_EMAIL_PATTERN = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)+$"
)


def is_valid_email(email: str) -> bool:
    if not isinstance(email, str) or len(email) > 254:
        return False

    local, separator, _ = email.rpartition("@")
    return (
        bool(separator)
        and len(local) <= 64
        and not local.startswith(".")
        and not local.endswith(".")
        and ".." not in local
        and bool(_EMAIL_PATTERN.fullmatch(email))
    )
