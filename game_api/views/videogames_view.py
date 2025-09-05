from rest_framework import viewsets, status
from ..models.videogames_model import VideoGame
from ..serializers.videogames_serializer import VideoGameSerializer
from rest_framework.response import Response

class VideoGameViewSet(viewsets.ModelViewSet):
    serializer_class = VideoGameSerializer
    queryset = VideoGame.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()

        return Response({"message": f"Videogame '{instance}' succesfully removed"}, status=status.HTTP_200_OK)