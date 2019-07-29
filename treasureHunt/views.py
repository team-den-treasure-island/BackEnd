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
        serializer = RoomSerializer(room)

        return Response(serializer.data)
