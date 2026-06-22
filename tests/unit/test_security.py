import pytest
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
    create_refresh_token,
    decode_token,
)


class TestSecurity:
    def test_password_hashing(self):
        password = "SecurePass123!"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("WrongPassword", hashed)

    def test_access_token_creation(self):
        data = {"sub": "user-123", "username": "test_user"}
        token = create_access_token(data)
        assert token is not None

        decoded = decode_token(token)
        assert decoded["sub"] == "user-123"
        assert decoded["username"] == "test_user"
        assert decoded["type"] == "access"

    def test_refresh_token_creation(self):
        data = {"sub": "user-123"}
        token = create_refresh_token(data)
        decoded = decode_token(token)
        assert decoded["type"] == "refresh"

    def test_invalid_token(self):
        decoded = decode_token("invalid.token.here")
        assert decoded is None

    def test_expired_token(self):
        pass
