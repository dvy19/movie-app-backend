from django.urls import path
from .views import CreateChatRoomView, ChatMessagesView

urlpatterns = [
    path('create-room/', CreateChatRoomView.as_view(), name='create-room'),

    path(
        '<uuid:room_id>/messages/',
        ChatMessagesView.as_view(),
        name='chat-messages'
    ),
]