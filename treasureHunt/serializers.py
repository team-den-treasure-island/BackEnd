from rest_framework import serializers

from .models import Player, Room


class PlayerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Player
        exclude = ("id",)


class RoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = Room
        exclude = ("id",)
