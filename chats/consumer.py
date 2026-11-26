
import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import Q

from .models import ChatRoom, Message


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):

        self.room_id = self.scope["url_route"]["kwargs"]["room_id"]
        self.user = self.scope["user"]

        if not self.user.is_authenticated:
            await self.close(code=4401)
            return

        is_member = await self.check_room_membership()

        if not is_member:
            await self.close(code=4403)
            return

        self.room_group_name = f"chat_{self.room_id}"

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        print(f"Connected: {self.user.id}, Room: {self.room_id}")

    @database_sync_to_async
    def check_room_membership(self):

        return ChatRoom.objects.filter(
            Q(user1=self.user) | Q(user2=self.user),
            id=self.room_id
        ).exists()

    async def disconnect(self, close_code):

        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(
                self.room_group_name,
                self.channel_name
            )

    async def receive(self, text_data):

        try:
            data = json.loads(text_data)
            content = data.get("message", "").strip()

            if not content:
                return

            # Save message in database
            message = await self.save_message(content)

            # Broadcast saved message
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "chat_message",
                    "message": {
                        "id": str(message["id"]),
                        "sender_id": message["sender_id"],
                        "content": message["content"],
                        "created_at": message["created_at"]
                    }
                }
            )

        except (json.JSONDecodeError, AttributeError):
            await self.send(text_data=json.dumps({
                "error": "Invalid message format"
            }))

    @database_sync_to_async
    def save_message(self, content):

        message = Message.objects.create(
            room_id=self.room_id,
            sender=self.user,
            content=content
        )

        return {
            "id": message.id,
            "sender_id": message.sender_id,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        }

    async def chat_message(self, event):

        await self.send(text_data=json.dumps({
            "message": event["message"]
        }))
