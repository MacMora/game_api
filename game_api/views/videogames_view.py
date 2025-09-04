from rest_framework import viewsets
from ..models.videogames_model import VideoGame
from ..serializers.videogames_serializer import VideoGameSerializer

class VideoGameViewSet(viewsets.ModelViewSet):
    serializer_class = VideoGameSerializer
    queryset = VideoGame.objects.all()