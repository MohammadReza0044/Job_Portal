import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed


def decode_jwt_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        print("Decoded payload:", payload)  # This should show role & email
        return payload
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed("Token expired")
    except jwt.InvalidTokenError:
        raise AuthenticationFailed("Invalid token")
