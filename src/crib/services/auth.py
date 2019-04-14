import logging

from flask_jwt_extended import create_access_token, create_refresh_token  # type: ignore
from werkzeug.security import (  # type: ignore
    check_password_hash,
    generate_password_hash,
)

from crib import exceptions, injection
from crib.domain.user import User

log = logging.getLogger(__name__)


class AuthService(injection.Component):
    user_repository = injection.Dependency()

    def register(self, username, password):
        if not (isinstance(password, str) and len(password) < 4):
            raise ValueError("Password should be a string of 4+ characters.")

        password = generate_password_hash(password)
        user = User(username=username, password=password)
        self.user_repository.add_user(user)

    def get_tokens(self, username, password):
        if not self._are_credentials_valid(username, password):
            return None

        return {
            "access_token": create_access_token(identity=username),
            "refresh_token": create_refresh_token(identity=username),
            "username": username,
        }

    def _are_credentials_valid(self, username, password):
        try:
            user = self.user_repository.get_user(username)
        except exceptions.EntityNotFound:
            return False

        return user.is_password_valid(password)
