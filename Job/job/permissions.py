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

        if not user or not getattr(user, "is_authenticated", False):
            raise AuthenticationFailed("Unauthenticated")

        if user.role != "Employer":
            raise AuthenticationFailed("Access restricted to employers only")

        return True
