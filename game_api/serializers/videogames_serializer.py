from rest_framework import serializers
from ..models.videogames_model import VideoGame

class VideoGameSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoGame
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')