from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .auth_user import AuthenticatedUser
from .jwt_decode import decode_jwt_token


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed("Authorization header missing or invalid")

        token = auth_header.split(" ")[1]
        payload = decode_jwt_token(token)
        if not payload:
            raise AuthenticationFailed("Invalid token")

        user = AuthenticatedUser(payload)
        return (user, None)  # request.user is now AuthenticatedUser
