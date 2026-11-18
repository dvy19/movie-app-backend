
import uuid

from django.db import models
from django.conf import settings


class ChatRoom(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    user1 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_rooms_as_user1"
    )

    user2 = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_rooms_as_user2"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user1", "user2"],
                name="unique_chat_participants"
            )
        ]

    @classmethod
    def get_or_create_room(cls, sender, recipient):
        """Retrieves an existing 1-on-1 room between two users or creates one.

        Sorting user IDs ensures order doesn't matter (User A & User B is the same
        room as User B & User A).
        """
        if sender == recipient:
            raise ValueError('Users cannot create a chat room with themselves.')

        # Sort users to maintain consistency in who is user1 vs user2
        # (Assuming your user primary keys can be compared, or use string representation of IDs)
        u1, u2 = sorted([sender, recipient], key=lambda u: str(u.id))

        room, created = cls.objects.get_or_create(user1=u1, user2=u2)
        return room, created

    def __str__(self):
        return f"Chat: {self.user1} - {self.user2}"


class Message(models.Model):

    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )

    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages"
    )

    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages"
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message by {self.sender}"
