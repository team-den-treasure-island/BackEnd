from treasureHunt.models import Player
from django.db.models.signals import post_save
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.forms.models import model_to_dict


@receiver(post_save, sender=Player)
def announce_updated_player(sender, instance, created, **kwargs):
    print("Hi")
    channel_layer = get_channel_layer()
    print(channel_layer)
    async_to_sync(channel_layer.group_send)(
        "update",
        {
            "type": "player.update",  # translated at consumer as room_update
            "event": "Player Update",
            "player": {**model_to_dict(instance), "cooldown": float(instance.cooldown)},
        },
    )
