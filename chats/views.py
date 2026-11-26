from django.shortcuts import render


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.contrib.auth import get_user_model

from .models import ChatRoom
import traceback
from .serializers import ChatRoomSerializer

from django.db.models import Q


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


    def get(self, request):

        try:
            print("========== CHAT ROOMS DEBUG ==========")
            print("Logged-in user:", request.user)
            print("Logged-in user ID:", request.user.id)

            rooms = ChatRoom.objects.filter(
                Q(user1=request.user) | Q(user2=request.user)
            ).select_related(
                "user1", "user2"
            ).order_by("-updated_at")

            print("Total rooms:", rooms.count())

            data = []

            for room in rooms:

                print("\nProcessing room:", room.id)
                print("User1:", room.user1)
                print("User2:", room.user2)

                other_user = (
                    room.user2 if room.user1_id == request.user.id
                    else room.user1
                )

                print("Other user:", other_user)
                print("Other user ID:", other_user.id)

                data.append({
                    "room_id": str(room.id),
                    "recipient_id": other_user.id,
                    "recipient_username": other_user.name,
                    "created_at": room.created_at,
                    "updated_at": room.updated_at
                })

            print("Final response:", data)
            print("========== END DEBUG ==========")

            return Response(data, status=status.HTTP_200_OK)

        except Exception as e:

            print("========== CHAT ROOMS ERROR ==========")
            print("Error:", str(e))
            traceback.print_exc()
            print("========== END ERROR ==========")

            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

