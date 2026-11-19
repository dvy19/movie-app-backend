from rest_framework import serializers
from .models import MoviePost
from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import MoviePost, Notification

User = get_user_model()


class PostAuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email"]  # Add "username" or "name" if your CustomUser has it
        read_only_fields = fields

class MoviePostSerializer(serializers.ModelSerializer):
    user = PostAuthorSerializer(read_only=True)
    likes_count = serializers.SerializerMethodField()
    comments_count = serializers.SerializerMethodField()

    class Meta:
        model = MoviePost
        fields = [
            "id",
            "user",
            "image",
            "title",
            "content",
            "category",
            "likes_count",
            "comments_count",
        ]
        read_only_fields = ["user"]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_comments_count(self, obj):
        return obj.comments.count()

class NotificationSerializer(serializers.ModelSerializer):
    sender_username = serializers.CharField(source='sender.username', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'sender_username', 'post', 'message', 'is_read', 'created_at']
        read_only_fields = ['id', 'recipient', 'sender', 'post', 'message', 'created_at']