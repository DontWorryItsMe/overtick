from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/sync/", consumers.SyncConsumer.as_asgi()),
]
