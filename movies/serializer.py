from rest_framework import serializers
from .models import MoviePost

class MoviePostSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoviePost
        fields = ['id', 'user', 'image', 'title', 'content', 'category']
        read_only_fields = ['user']