from django.urls import path
from WebSocketChannel import consumer

websocket_urlpatterns = [
    path('ws/chat/<str:chatName>/', consumer.ChatConsumer.as_asgi()),
    path('ws/notifications/', consumer.NotificationConsumer.as_asgi()),
]
