from ..models.videogames_model import VideoGame
from ..serializers.videogames_serializer import VideoGameSerializer
from ..permissions import WriteRequiresAPIKey

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.renderers import JSONRenderer
from rest_framework.parsers import JSONParser
from rest_framework.throttling import ScopedRateThrottle

class VideoGameViewSet(viewsets.ModelViewSet):
    serializer_class = VideoGameSerializer
    queryset = VideoGame.objects.all().order_by('-created_at')

    renderer_classes = [JSONRenderer]
    parser_classes = [JSONParser]

    permission_classes = [AllowAny & WriteRequiresAPIKey]

    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "videogames"

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response({"message": f"Videogame '{instance}' succesfully removed"}, status=status.HTTP_200_OK)