from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404
from django.http import Http404

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


class GetWorldView(APIView):
    def get(self):
        rooms = list(Room.object.all())
        response_obj = {}
        for room in rooms:
            room_obj = {}
            exits_dict = {}
            exits = {}
            if room["n_to"]:
                exits["n"] = room["n_to"]
            if room["s_to"]:
                exits["s"] = room["s_to"]
            if room["e_to"]:
                exits["e"] = room["e_to"]
            if room["w_to"]:
                exits["w"] = room["w_to"]

            room_obj['exits'] = exits
            room_obj['room_id'] = room['room_id']
            room_obj['title'] = room['title']
            room_obj['description'] = room['description']
            room_obj['coordinates'] = tuple(
                room['coord_x'], room['coord_y'])
            room_obj['elevation'] = room['elevation']
            room_obj['terrain'] = room['terrain']

            response_obj[room['room_id']] = room_obj

        return Response(response_obj)
