from django.conf.urls import url
from . import consumers

# channel routing config for treasureHunt to route
# to the proper consumers
websocket_urlpatterns = [
    url(r"^ws/updates/", consumers.UpdateConsumer)
]
