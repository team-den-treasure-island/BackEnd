from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import treasureHunt.routing

# when a connection is made to the server, ProtocolTypRouter will
# first inspect the type of connection

# if it is a websocket connection (ws:// or wss://), the connection
# is passed to the AuthMiddlewareStack


# the AuthMiddlewareStack will populate the connection's scope with
# a reference to the currently authenticated user
# after which it will go to the URL router

# the URLRouter will examine the http path of the connection to
# route it to a particular consumer based on the provided url patterns
application = ProtocolTypeRouter(
    {"websocket": AuthMiddlewareStack(URLRouter(treasureHunt.routing.websocket_urlpatterns))}
)
