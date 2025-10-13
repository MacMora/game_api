from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.http import JsonResponse
import logging

logger = logging.getLogger(__name__)

class BlacklistTokenMiddleware:
    """
    Middleware para validar que los tokens de acceso no estén en la blacklist
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Verificar si hay un token de autorización en el header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            
            try:
                # Decodificar el token para obtener el jti
                token = AccessToken(access_token)
                jti = token.payload.get('jti')
                
                # Verificar si el token está en la blacklist
                if jti:
                    # Buscar en OutstandingToken con el jti
                    outstanding_token = OutstandingToken.objects.filter(jti=jti).first()
                    if outstanding_token and BlacklistedToken.objects.filter(token=outstanding_token).exists():
                        logger.warning(f"Token blacklisted detected: {jti} for user {outstanding_token.user.username}")
                        return JsonResponse({
                            'error': 'Token ha sido invalidado. Por favor, inicie sesión nuevamente.',
                            'detail': 'Este token ha sido revocado y ya no puede ser utilizado.'
                        }, status=401)
                    
            except (TokenError, InvalidToken) as e:
                # Si el token es inválido, dejamos que Django REST Framework lo maneje
                logger.debug(f"Token validation error: {e}")
                pass

        response = self.get_response(request)
        return response
