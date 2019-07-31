from django.db import models
from uuid import uuid4

# from django.contrib.auth.models import User

# Create your models here.


class Player(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=255, editable=True)
    current_room = models.IntegerField(default=0)
    cooldown = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    explore_mode = models.BooleanField(default=False)
    encumbrance = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    gold = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class Room(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    room_id = models.IntegerField()
    coord_x = models.SmallIntegerField(blank=True, null=True, default=None)
    coord_y = models.SmallIntegerField(blank=True, null=True, default=None)
    elevation = models.IntegerField(blank=True, null=True, default=None)
    terrain = models.CharField(max_length=255, blank=True, null=True, default=None)
    n_to = models.IntegerField(default=None, blank=True, null=True)
    s_to = models.IntegerField(default=None, blank=True, null=True)
    e_to = models.IntegerField(default=None, blank=True, null=True)
    w_to = models.IntegerField(default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Room: " + str(self.room_id)
