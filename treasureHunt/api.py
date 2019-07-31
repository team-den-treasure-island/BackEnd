from rest_framework import serializers, viewsets
from .models import Room, Player

# convention is to name the serializer classes after what they
# are serializing


class RoomSerializer(serializers.HyperlinkedModelSerializer):
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
        fields = ("__all__")


# has access to request directly
class RoomViewSet(viewsets.ModelViewSet):
    serializer_class = RoomSerializer
    queryset = Room.objects.none() # empty dictionary

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
        fields = ("__all__")


# has access to request directly
class PlayerViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerSerializer
    queryset = Player.objects.none() # empty dictionary

    def get_queryset(self):
        # user = self.request.user
        return Player.objects.all()

        # built in auth apparently has an is_anonymous
        # if user.is_anonymous:
        #     # return none if they're anonymous
        #     return Player.objects.none()
        # else:
        #     return Player.objects.filter(user=user)

