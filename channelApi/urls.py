from django.urls import path
from .view import RedisChannelListView, RedisChannelMessagesView, RedisChannelMessageDeleteView, RedisUnreadCountView

urlpatterns = [
    path('channels/', RedisChannelListView.as_view(), name='channel-list'),
    path('messages/<str:chatFullId>/', RedisChannelMessagesView.as_view(), name='channel-messages'),
    path('mentioned-messages/<str:idUserMentioned>/', RedisChannelMessagesView.as_view(), name='mentioned-messages'),
    path("delete/<str:chatFullId>/<str:id_redis>/", RedisChannelMessageDeleteView.as_view(), name='delete'),
    path('channels/mss-counts/', RedisUnreadCountView.as_view(), name='channel-mss-counts'),

]
