from django.conf import settings
from graphene_django import DjangoObjectType
import graphene
from .models import Room, Player


# connect model to class Room
class Room(DjangoObjectType):
    class Meta:
        model = Room  # which model to export for Graphene
        interfaces = (graphene.relay.Node,)  # type of entity

# connect model to class Player
class Player(DjangoObjectType):
    class Meta:
        model = Player  # which model to export for Graphene
        interfaces = (graphene.relay.Node,)  # type of entity

# connect Room to query
class Query(graphene.ObjectType):

    # this class property must match the resolve methodname
    rooms = graphene.List(Room)

    # this class property must match the resolve methodname
    players = graphene.List(Player)

    # must match the property above
    # also names the resource for the graphql query
    def resolve_rooms(self, info):
        user = info.context.user # similar to api.py

        if user.is_anonymous:
            return Room.objects.none()
        else:
            return Room.objects.filter(user=user)

    def resolve_players(self, info):
        user = info.context.user # similar to api.py

        if user.is_anonymous:
            return Player.objects.none()
        else:
            return Player.objects.filter(user=user)

# expose query to graphene
schema = graphene.Schema(query=Query)

