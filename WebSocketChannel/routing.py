from django.urls import path
from WebSocketChannel import consumer

websocket_urlpatterns = [
    path('ws/chat/', consumer.ChatConsumer.as_asgi()),
]
