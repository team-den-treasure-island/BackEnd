from django.db import models

# Create your models here.


class Player(models.Model):
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
    room_id = models.IntegerField()
    coord_x = models.SmallIntegerField(blank=True)
    coord_y = models.SmallIntegerField(blank=True)
    elevation = models.IntegerField(blank=True)
    terrain = models.CharField(max_length=255, blank=True)
    n_to = models.IntegerField(default=0)
    s_to = models.IntegerField(default=0)
    e_to = models.IntegerField(default=0)
    w_to = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return 'Room: ' + str(self.room_id)
