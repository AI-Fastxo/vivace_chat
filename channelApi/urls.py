from django.urls import path
from .view import RedisChannelListView

urlpatterns = [
    path('channels/', RedisChannelListView.as_view(), name='channel-list'),
]
