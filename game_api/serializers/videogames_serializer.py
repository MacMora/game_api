#from turtle import title
from rest_framework import serializers
from ..models.videogames_model import VideoGame
from django.utils.text import slugify

class VideoGameSerializer(serializers.ModelSerializer):

    class Meta:
        model = VideoGame
        fields = '__all__'
        read_only_fields = ('id', 'created_at', 'updated_at')

    def validate_title(self, value):
        v = " ".join(value.split())
        if any(ch in v for ch in "!@#$%^&*()_+=[]{}|;:'\",.<>?/\\`~"):
            raise serializers.ValidationError("Title must not contain special characters.")
        return v

    def validate_price(self, value):
        if value < 0:
            raise serializers.ValidationError("Price must be a non-negative integer.")
        return value
    
    def create(self, validated_data):
        obj = VideoGame(**validated_data)
        obj.slug = slugify(obj.title)[:50]
        obj.save()
        return obj
    
    def update(self, instance, validated_data):
        validated_data.pop("created_at", None)
        return super().update(instance, validated_data)