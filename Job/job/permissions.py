from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission


class IsJWTAuthenticated(BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user or not isinstance(user, dict):
            raise AuthenticationFailed("Unauthenticated or invalid token")
        return True


class IsEmployer(BasePermission):
    def has_permission(self, request, view):
        user = request.user

        if not user or not isinstance(user, dict):
            raise AuthenticationFailed("Invalid or missing user")

        return user.get("role") == "Employer"
