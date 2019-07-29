import requests
import json
import time
import os

content = ""
with open("key.txt", "r") as infile:
    content = infile.readlines()

content = [x.strip() for x in content]
my_key = content[0]
url = "https://lambda-treasure-hunt.herokuapp.com/api/adv"
headers = {"content-type": "application/json", "Authorization": f"Token {my_key}"}
cooldon = 0

roomGraph = {}
# init
# response:
# {
#     "room_id": 0,
#     "title": "A brightly lit room",
#     "description": "You are standing in the center of a brightly lit room. You notice a shop to the west and exits to the north, south and east.",
#     "coordinates": "(60,60)",
#     "elevation": 0,
#     "terrain": "NORMAL",
#     "players": [
#         "player81",
#         "player94",
#         "player119",
#         "player138",
#         "player136",
#     ],
#     "items": [],
#     "exits": ["n", "s", "e", "w"],
#     "cooldown": 1.0,
#     "errors": [],
#     "messages": [],
# }

# Error Response (400):
#
# {"cooldown": 5.447648, "errors": ["Cooldown Violation: +5s CD"]}

def init(key):
    r = requests.get(f"{ url }/init", headers=headers)
    return r


def move(key, direction, next_room):
    r = requests.post(f"{ url }/move", {"direction": direction}, headers=headers)
    return r

# load roomgraph from json if it exists
def load_roomgraph():
    if not os.path.isfile('roomgrpah.json'):
        return {}
    with open('roomgraph.json', 'w') as f:
        return json.load(f)

# dump roomgraph to json
def save_roomgraph():
    with open('roomgraph.json', 'w') as f:
        json.dump(roomGraph, f)

####### PROGRAM START ########
roomGraph = load_roomgraph()
player = {}
direction_opposites = {"n": "s", "e": "w", "s": "n", "w": "e"}
initial_exits = {}

# initialize the player
r = init(my_key)
rjson = r.json()

# if the request fails, sleep the cooldown + half a sec and try again
while True:
    cooldown = rjson['cooldown']
    if r.status_code is not 200:
        print("Init statuscode not 200")
        time.sleep(cooldown + 0.5)
    else:
        time.sleep(cooldown + 0.5)
        break

player['current_room'] = {
    'exits': rjson[ 'exits' ],
    "room_id": rjson['room_id'],
    "title": rjson["title"],
    "description": rjson["description"],
    "coordinates": rjson["coordinates"],
    "elevation": rjson["elevation"],
    "terrain": rjson["terrain"],
    "exits": rjson["exits"]
}

roomGraph[rjson['room_id']] = player['current_room']
save_roomgraph()
breakpoint()

# main traversal loop
# 500 rooms
while len(graph) < 500:
    pass
