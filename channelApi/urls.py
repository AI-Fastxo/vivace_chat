from django.urls import path
from .view import RedisChannelListView, RedisChannelMessagesView

urlpatterns = [
    path('channels/', RedisChannelListView.as_view(), name='channel-list'),
    path('messages/<str:chatFullId>/', RedisChannelMessagesView.as_view(), name='channel-messages'),
    path('mentioned-messages/<str:idUserMentioned>/', RedisChannelMessagesView.as_view(), name='mentioned-messages'),
]
