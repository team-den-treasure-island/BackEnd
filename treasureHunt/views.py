from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.http import Http404
import requests

from .serializers import RoomSerializer, PlayerSerializer
from .models import Player, Room

# Create your views here.


class RoomDetailsView(APIView):

    def get_object(self, pk):
        try:
            return Room.objects.get(room_id=pk)

        except Room.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        room = self.get_object(pk)
        serialize = RoomSerializer(room)

        return Response(serialize.data)

    def post(self, request, format=None):
        serialize = RoomSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        room = self.get_object(pk)
        serialize = RoomSerializer(room, data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        room = self.get_object(pk)
        room.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        room = self.get_object(pk)
        serialize = RoomSerializer(room, data=request.data, partial=True)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)


class PlayerDetailsView(APIView):
    def get_object(self, pk):
        try:
            return Player.objects.get(pk=pk)

        except Player.DoesNotExist:
            raise Http404

    def get(self, request, pk, format=None):
        room = self.get_object(pk)
        serialize = PlayerSerializer(room)

        return Response(serialize.data)

    def post(self, request, format=None):
        serialize = PlayerSerializer(data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data, status=status.HTTP_201_CREATED)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk, format=None):
        player = self.get_object(pk)
        serialize = PlayerSerializer(player, data=request.data)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        player = self.get_object(pk)
        player.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def patch(self, request, pk, format=None):
        player = self.get_object(pk)
        serialize = PlayerSerializer(player, data=request.data, partial=True)
        if serialize.is_valid():
            serialize.save()
            return Response(serialize.data)
        return Response(serialize.errors, status=status.HTTP_400_BAD_REQUEST)

    class PlayerInitView(APIView):
        mapping = {
            "4b0963db718e09fbe815d75150d98d79d9a243bb": "kittendaddy69",
            "5d57a24ad7c366fb7c3de0db9a2d7f1ccd6aaacf": "anon_denlife_loyalist",
            "11fca1909b41121878367faa97cc6e92a3286cf0": "DenLifeZero",
            "1862aa8dfe43381b4fbbdbbc5a83397e65824b54": "goose_h8r",
            "203ef3ef95a3e8c6ef25faa74f40cc384d6378ec": "strugglebusallday"
        }

        def update_player(self, update, pk):
            player = Player.objects.get(mapping[pk]=name)
            player.current_room = update["room_id"]
            player.cooldown = update["cooldown"]

            return player

        def get(self, pk, format=None):
            url = 'https://lambda-treasure-hunt.herokuapp.com/api/adv/init/'
            access_token = pk
            try:
                result = requests.get(url, headers={
                    'Content-Type': 'application/json', 'Authorization': 'Token {}'.format(access_token)})
                response = r.json()
                updated = self.update_player(response, pk)
                updated['key'] = pk
                return Response(updated)
