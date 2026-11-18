from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from .models import ChatRoom
from .serializers import ChatRoomSerializer

User = get_user_model()


class CreateChatRoomView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        recipient_id = request.data.get("recipient_id")

        if not recipient_id:
            return Response(
                {"error": "Recipient ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            recipient = User.objects.get(id=recipient_id)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            room, created = ChatRoom.get_or_create_room(
                sender=request.user,
                recipient=recipient
            )

        except ValueError as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ChatRoomSerializer(room)

        return Response(
            {
                "message": "Chat room created" if created else "Existing chat room retrieved",
                "created": created,
                "room": serializer.data
            },
            status=status.HTTP_200_OK
        )

