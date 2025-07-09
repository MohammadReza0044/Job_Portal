from django.conf import settings
from rest_framework.permissions import BasePermission


class IsInternalService(BasePermission):
    def has_permission(self, request, view):
        token = request.headers.get("X-Service-Token")
        return token == settings.INTERNAL_SERVICE_TOKEN
