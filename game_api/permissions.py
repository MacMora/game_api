from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticated
from django.conf import settings

class IsAuthenticatedOrReadOnly(BasePermission):
    """
    GET -> permitido para todos
    POST/PUT/DELETE -> requieren autenticación JWT
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated
