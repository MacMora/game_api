from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from django.contrib.auth import authenticate
from django.db import transaction
from ..models.user_model import CustomUser
from ..serializers.user_serializer import UserSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [AllowAny]
    
    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        """
        if self.action in ['list', 'create', 'destroy']:
            permission_classes = [IsAdminUser]  # Solo superuser
        elif self.action in ['update', 'partial_update', 'retrieve']:
            permission_classes = [IsAuthenticated]  # Usuario autenticado
        elif self.action == 'profile':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [AllowAny]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        """
        Filtra el queryset según los permisos del usuario
        """
        if self.request.user.is_superuser:
            return CustomUser.objects.all()
        elif self.request.user.is_authenticated:
            # Usuarios autenticados solo pueden ver su propio perfil
            return CustomUser.objects.filter(id=self.request.user.id)
        else:
            return CustomUser.objects.none()

    def get_object(self):
        """
        Asegura que los usuarios solo puedan acceder a su propio objeto
        """
        obj = super().get_object()
        if not self.request.user.is_superuser:
            if obj.id != self.request.user.id:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("No tienes permisos para acceder a este usuario.")
        return obj

    def list(self, request, *args, **kwargs):
        """
        Solo superusers pueden listar todos los usuarios
        """
        return super().list(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        """
        Solo superusers pueden crear usuarios directamente
        """
        return super().create(request, *args, **kwargs)

    def retrieve(self, request, *args, **kwargs):
        """
        Usuarios solo pueden ver su propio perfil, superusers pueden ver todos
        """
        return super().retrieve(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        """
        Usuarios solo pueden actualizar su propio perfil, superusers pueden actualizar todos
        """
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        """
        Usuarios solo pueden actualizar parcialmente su propio perfil, superusers pueden actualizar todos
        """
        return super().partial_update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        """
        Solo superusers pueden eliminar usuarios
        """
        return super().destroy(request, *args, **kwargs)

    def _invalidate_all_user_tokens(self, user):
        """
        Invalida todos los tokens existentes de un usuario
        """
        try:
            with transaction.atomic():
                # Obtener todos los tokens pendientes del usuario
                outstanding_tokens = OutstandingToken.objects.filter(user=user)
                
                # Blacklistear todos los tokens pendientes
                for token in outstanding_tokens:
                    # Verificar si el token ya está en blacklist
                    if not BlacklistedToken.objects.filter(token=token).exists():
                        BlacklistedToken.objects.create(token=token)
                    
        except Exception as e:
            # Si hay algún error, continuamos sin fallar
            # En producción, podrías loggear este error
            pass

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """Registro de nuevos usuarios"""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Invalidar tokens existentes antes de crear nuevos
            self._invalidate_all_user_tokens(user)
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'is_superuser': user.is_superuser,
                    'is_active': user.is_active,
                    'created_at': user.created_at,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """Login de usuarios"""
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not username or not password:
            return Response({
                'error': 'Username y password son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if user is not None:
            if user.is_active:
                # Invalidar tokens existentes antes de crear nuevos
                self._invalidate_all_user_tokens(user)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'message': 'Login exitoso - tokens anteriores invalidados',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'is_superuser': user.is_superuser,
                        'is_active': user.is_active,
                        'created_at': user.created_at,
                    },
                    'tokens': {
                        'access': str(refresh.access_token),
                        'refresh': str(refresh),
                    }
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': 'Usuario inactivo'
                }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request):
        """Obtener información del perfil del usuario autenticado"""
        user = request.user
        serializer = self.get_serializer(user)
        return Response({
            'message': 'Perfil obtenido exitosamente',
            'user': serializer.data
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Logout del usuario - invalida todos los tokens usando el access token"""
        try:
            # Obtener el token de autorización del header
            auth_header = request.headers.get('Authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return Response({
                    'error': 'Token de autorización requerido'
                }, status=status.HTTP_401_UNAUTHORIZED)
            
            # Extraer el access token
            access_token = auth_header.split(' ')[1]
            
            try:
                # Validar el access token
                token = AccessToken(access_token)
                user_id = token.payload.get('user_id')
                
                # Obtener el usuario
                user = CustomUser.objects.get(id=user_id)
                
                # Invalidar todos los tokens del usuario
                self._invalidate_all_user_tokens(user)
                
                return Response({
                    'message': 'Logout exitoso - todos los tokens han sido invalidados'
                }, status=status.HTTP_200_OK)
                
            except (TokenError, InvalidToken, CustomUser.DoesNotExist):
                return Response({
                    'error': 'Token de acceso inválido'
                }, status=status.HTTP_401_UNAUTHORIZED)
                
        except Exception as e:
            return Response({
                'error': 'Error durante el logout'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def refresh_token(self, request):
        """Renovar tokens de acceso"""
        refresh_token = request.data.get('refresh_token') or request.headers.get('refresh-token')
        
        if not refresh_token:
            return Response({
                'error': 'Refresh token es requerido'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            token = RefreshToken(refresh_token)
            user_id = token.payload.get('user_id')
            user = CustomUser.objects.get(id=user_id)
            
            # Invalidar todos los tokens existentes del usuario
            self._invalidate_all_user_tokens(user)
            
            # Crear nuevos tokens
            new_refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'Tokens renovados exitosamente - tokens anteriores invalidados',
                'tokens': {
                    'access': str(new_refresh.access_token),
                    'refresh': str(new_refresh),
                }
            }, status=status.HTTP_200_OK)
            
        except (TokenError, InvalidToken, CustomUser.DoesNotExist):
            return Response({
                'error': 'Refresh token inválido'
            }, status=status.HTTP_401_UNAUTHORIZED)