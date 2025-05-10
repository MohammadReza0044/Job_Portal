from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from utils.jwt_decode import decode_jwt_token


class JWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return None
        token = auth_header.split(" ")[1]
        try:
            user_data = decode_jwt_token(token)
            return (user_data, None)
        except AuthenticationFailed:
            raise AuthenticationFailed("Invalid JWT")
