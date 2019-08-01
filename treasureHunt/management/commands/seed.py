# <project>/<app>/management/commands/seed.py
from django.core.management.base import BaseCommand
from treasureHunt.models import Room
import json
import os
from ast import literal_eval as make_tuple

# import random

# python manage.py seed

# """ Clear all data and creates addresses """
# MODE_REFRESH = 'refresh'
#
# """ Clear all data and do not create any object """
# MODE_CLEAR = 'clear'


class Command(BaseCommand):
    help = "seed database for testing and development."

    def handle(self, *args, **options):
        self.stdout.write("seeding data...")
        run_seed(self)
        self.stdout.write("done.")


# def clear_data():
#     """Deletes all the table data"""
#     logger.info("Delete Address instances")
#     Address.objects.all().delete()
#
#
# def create_address():
#     """Creates an address object combining different elements from the list"""
#     logger.info("Creating address")
#     street_flats = ["#221 B", "#101 A", "#550I", "#420G", "#A13"]
#     street_localities = ["Bakers Street", "Rajori Gardens", "Park Street", "MG Road", "Indiranagar"]
#     pincodes = ["101234", "101232", "101231", "101236", "101239"]
#
#     address = Address(
#         street_flat=random.choice(street_flats),
#         street_locality=random.choice(street_localities),
#         pincode=random.choice(pincodes),
#     )
#     address.save()
#     logger.info("{} address created.".format(address))
#     return address

# Room:
    # id         = models.UUIDField(primary_key      = True, default = uuid4, editable = False)
    # room_id    = models.IntegerField()
    # coord_x    = models.SmallIntegerField(blank    = True)
    # coord_y    = models.SmallIntegerField(blank    = True)
    # elevation  = models.IntegerField(blank         = True)
    # terrain    = models.CharField(max_length       = 255, blank    = True)
    # n_to       = models.IntegerField(default       = 0)
    # s_to       = models.IntegerField(default       = 0)
    # e_to       = models.IntegerField(default       = 0)
    # w_to       = models.IntegerField(default       = 0)
    # created_at = models.DateTimeField(auto_now_add = True)
    # updated_at = models.DateTimeField(auto_now     = True)

# JSON format:
  # "10": {
  #   "exits": { "n": 19, "s": 0, "w": 43 },
  #   "room_id": "19",
  #   "title": "A misty room",
  #   "description": "You are standing on grass and surrounded by a dense mist. You can barely make out the exits in any direction.",
  #   "coordinates": "(60,62)",
  #   "elevation": 0,
  #   "terrain": "NORMAL"
  # },


def run_seed(self):
    with open(
        f"{os.path.dirname(os.path.realpath(__file__))}/roomgraph.json", "r"
    ) as f:
        Room.objects.all().delete()
        data = json.load(f)
        new_rooms = []
        for k in data:
            # make a new room
            this_room = data[k]
            # breakpoint()
            coords = make_tuple(this_room["coordinates"])
            new_room = Room(
                room_id=k,
                coord_x=coords[0],
                coord_y=coords[1],
                elevation=this_room.get("elevation"),
                terrain=this_room.get("terrain"),
                n_to=this_room.get("exits").get("n"),
                e_to=this_room.get("exits").get("e"),
                s_to=this_room.get("exits").get("s"),
                w_to=this_room.get("exits").get("w"),
                description=this_room.get("description"),
                title=this_room.get("title")
            )
            new_rooms.append(new_room)
        Room.objects.bulk_create(new_rooms)

    # print(os.path.dirname(os.path.realpath(__file__)))
    # """ Seed database based on mode
    #
    # :param mode: refresh / clear
    # :return:
    # """
    # # Clear data from tables
    # clear_data()
    # if mode == MODE_CLEAR:
    #     return
    #
    # # Creating 15 addresses
    # for i in range(15):
    #     create_address()
