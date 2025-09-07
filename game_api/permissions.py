from rest_framework.permissions import BasePermission, SAFE_METHODS
from django.conf import settings

class WriteRequiresAPIKey(BasePermission):
    """
    GET -> permitido
    POST/PUT/DELETE -> requieren API-Key válida
    """
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        api_key = request.headers.get("x-api-key")
        return api_key and api_key == getattr(settings, "PROJECT_API_KEY", "")
