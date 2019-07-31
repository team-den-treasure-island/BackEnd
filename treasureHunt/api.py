from rest_framework import serializers, viewsets
from .models import Room, Player
from collections import OrderedDict
from rest_framework.permissions import BasePermission, IsAuthenticatedOrReadOnly
from rest_framework.authentication import TokenAuthentication


# convention is to name the serializer classes after what they
# are serializing


# class Token

class RoomSerializer(serializers.HyperlinkedModelSerializer):
    # lookup_field = 'room_id'

    def create(self, validated_data):
        # import pdb
        #
        # pdb.set_trace()
        # pass

        # user = self.context['request'].user
        room = Room.objects.create(**validated_data)
        return room

    class Meta:
        model = Room
        lookup_field = "room_id"
        fields = "__all__"
        extra_kwargs = {"url": {"lookup_field": "room_id"}}

    def to_representation(self, instance):
        result = super().to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])


# has access to request directly
class RoomViewSet(viewsets.ModelViewSet):
    # can bitwise operate on these permission classes
    # want permission to be either token or session
    # permission_classes = [TokenAuthentication | IsAuthenticatedOrReadOnly]
    serializer_class = RoomSerializer
    queryset = Room.objects.none()  # empty dictionary
    lookup_field = "room_id"

    def get_queryset(self):
        # user = self.request.user

        return Room.objects.all()
        # # built in auth apparently has an is_anonymous
        # if user.is_anonymous:
        #     # return none if they're anonymous
        #     return Room.objects.none()
        # else:
        #     return Room.objects.filter(user=user)


class PlayerSerializer(serializers.HyperlinkedModelSerializer):
    def create(self, validated_data):
        # import pdb
        #
        # pdb.set_trace()
        # pass

        # user = self.context['request'].user
        player = Player.objects.create(**validated_data)
        return player

    class Meta:
        model = Player
        fields = "__all__"
        lookup_field = "name"
        extra_kwargs = {"url": {"lookup_field": "name"}}


# has access to request directly
class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.none()  # empty dictionary
    lookup_field = "name"

    def get_queryset(self):
        # user = self.request.user
        return Player.objects.all()

        # built in auth apparently has an is_anonymous
        # if user.is_anonymous:
        #     # return none if they're anonymous
        #     return Player.objects.none()
        # else:
        #     return Player.objects.filter(user=user)
