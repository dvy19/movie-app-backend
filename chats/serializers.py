from rest_framework import serializers
from .models import ChatRoom, Message


class ChatRoomSerializer(serializers.ModelSerializer):

    user1 = serializers.StringRelatedField(read_only=True)
    user2 = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = ChatRoom
        fields = [
            'id',
            'user1',
            'user2',
            'created_at',
            'updated_at'
        ]
        read_only_fields = fields


class MessageSerializer(serializers.ModelSerializer):

    sender = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Message
        fields = [
            'id',
            'room',
            'sender',
            'content',
            'created_at',
            'is_read'
        ]
        read_only_fields = [
            'id',
            'sender',
            'created_at',
            'is_read'
        ]