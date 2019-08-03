import requests
import json
import time
import os
import sys
import random
import datetime
from decouple import config


class Queue:
    def __init__(self):
        self.queue = []

    def enqueue(self, value):
        self.queue.append(value)

    def dequeue(self):
        if self.size() > 0:
            return self.queue.pop(0)
        else:
            return None

    def size(self):
        return len(self.queue)


backend_token = config("BACKEND_TOKEN")
backend_headers = {"content-type": "application/json", "Authorization": backend_token}
name_mappings = None
with open("name_mappings.json", "r") as f:
    name_mappings = json.load(f)

my_key = ""
if os.path.isfile("key.txt"):
    with open("key.txt", "r") as infile:
        my_key = infile.readlines()[0].strip()

if len(sys.argv) >= 2:
    my_key = sys.argv[1].strip()

my_name = name_mappings[my_key]
print(f"My Name is {my_name}")
if len(my_key) == 0 or len(my_name) == 0:
    print("no key or matching name for that key!")
    exit()

url = config("TREASURE_HUNT_URL")
backend_url = config("BACKEND_URL")
headers = {"content-type": "application/json", "Authorization": f"Token {my_key}"}
cooldown = 0
player = {}
player["encumbered"] = False
player["max_weight"] = False

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
def create_player(name, move_data):
    r = requests.post(
        f"{ backend_url }players/",
        json={
            "name": name,
            "current_room": move_data["room_id"],
            "cooldown": move_data["cooldown"]
        },
        headers=backend_headers,
    )
    return r

def update_player(name, move_data):
    response = requests.put(
        f"{ backend_url }players/{name}/",
        json={
            "name": name,
            "current_room": move_data["room_id"],
            "cooldown": move_data["cooldown"]
        },
        headers=backend_headers,
    )
    if response.status_code == 404:
        create_player(name, move_data)
    return response



def change_name(key, name):
    r = requests.post(
        f"{ url }/change_name", json={"name": name, "confirm": "aye"}, headers=headers
    )
    return r


def pretty_print(ugly_json):
    print(json.dumps(ugly_json, indent=4, sort_keys=True))

def init(key):
    r = requests.get(f"{ url }/init", headers=headers)
    return r


def transmogrify(name):
    r = requests.post(
        f"{ url }/transmogrify",
        json={"name": name},
        headers=headers,
    )
    return r



def move(key, direction, next_room):
    r = requests.post(
        f"{ url }/move",
        json={"direction": direction, "next_room_id": str(next_room)},
        headers=headers,
    )
    update_player(my_name, r.json())
    return r

def pray(key):
    r = requests.post(
        f"{ url }/pray",
        data={},
        headers=headers,
    )
    return r

def flight(key, direction):
    r = requests.post(
        f"{ url }/pray",
        json={"direction": direction},
        headers=headers,
    )
    return r

def dash(key, direction, num_rooms, next_room_ids):
    r = requests.post(
        f"{ url }/dash",
        json={"direction": direction, "num_rooms": num_rooms, "next_room_ids": ",".join(next_room_ids)},
        headers=headers,
    )
    return r


def sell(key, name):
    r = requests.post(
        f"{ url }/sell", json={"name": name, "confirm": "yes"}, headers=headers
    )
    return r


def pickup(key, name):
    r = requests.post(f"{ url }/take", json={"name": name}, headers=headers)
    return r


def get_status(key):
    r = requests.post(f"{ url }/status", data={}, headers=headers)
    return r

def drop(key, name):
    r = requests.post(f"{ url }/drop", json={"name": name}, headers=headers)
    return r


# load roomgraph from json if it exists
def load_roomgraph(filename=None):
    result = {}
    if filename is None:
        filename = "roomgraph.json"
    if not os.path.isfile(filename):
        return {}

    with open(filename, "r") as f:
        result = json.load(f)
    return result


# reshape move response
def shape_move_response(response, roomGraph):
    result = {
        "exits": {d: None for d in response["exits"]},
        "room_id": f"{response['room_id']}",
        "title": response["title"],
        "description": response["description"],
        "coordinates": response["coordinates"],
        "elevation": response["elevation"],
        "terrain": response["terrain"],
    }
    if result["room_id"] in roomGraph:
        existing_exits = roomGraph[result["room_id"]]["exits"]
        for k in existing_exits:
            if k not in result["exits"] or result["exits"][k] is None:
                result["exits"][k] = f"{existing_exits[k]}"
    return result


# dump roomgraph to json
def save_roomgraph(roomGraph=None):
    with open("roomgraph.json", "w") as f:
        json.dump(roomGraph, f)


# convert from old format
# if the map changes, this will probably be wrong
def load_old_data(filename=None):
    if filename is None:
        filename = "data.json"
    roomGraph = load_roomgraph()
    old_roomgraph = load_roomgraph(filename)
    for k in old_roomgraph:
        if f"{k}" in roomGraph:
            roomGraph[f"{k}"]["exits"] = old_roomgraph[k][1]
        else:
            roomGraph[f"{k}"] = {
                "exits": old_roomgraph[k][1],
                "room_id": k,
                "coordinates": f"({old_roomgraph[k][0]['x']},{old_roomgraph[k][0]['y']})",
            }
    # Overwrites the old roomgraph
    save_roomgraph(roomGraph)
    return roomGraph


# bfs to find the shortest route
def find_shortest_path(start_id, end_id, roomGraph, explore_nones=None):
    if explore_nones is None:
        explore_nones = True
    # we're already there!
    if start_id == end_id:
        return []

    current_room = roomGraph[start_id]
    while True:
        visited = set()
        # create the queue
        q = Queue()

        # add our current neighbors
        for k, v in current_room["exits"].items():
            # queue an initial path list with this first move
            q.enqueue([(f"{k}", v)])

        # while our queue length is > 0, search until we find a room_id match
        while q.size() > 0:
            path = q.dequeue()
            t = path[-1]
            room_id = f"{t[1]}"
            room_direction = t[0]
            if t[1] is None:
                continue

            # if room_id is "None"
            # unexplored route, explore it
            if room_id is "None":
                if explore_nones:
                    return path
                else:
                    # skip this path
                    continue

            # if we found the path, return it
            if room_id == end_id:
                return path

            if len(visited) == len(roomGraph):
                print("Ran out of rooms trying to find path!")
                exit()

            if room_id not in visited:
                # add it
                visited.add(room_id)
                # queue up neighbors
                if room_id in roomGraph:
                    for k, v in roomGraph[room_id]["exits"].items():
                        path_copy = list(path)
                        path_copy.append((k, v))
                        q.enqueue(path_copy)


# Move to the shop
def go_sell(key, player, roomGraph):
    print("Going to sell.")
    while True:
        current_id = player["current_room"]["room_id"]
        shortest_route = find_shortest_path(current_id, "1", roomGraph)
        if len(shortest_route) == 0:
            # we're already there
            break
        r = None
        print(f"Shortest Route: {shortest_route}")
        while r is None or len(r.json()["errors"]) > 0:
            print(f"Moving to {shortest_route[0][0]}, {shortest_route[0][1]}")
            r = move(my_key, shortest_route[0][0], shortest_route[0][1])
            rjson = r.json()
            cooldown = rjson["cooldown"]
            print(f"Sleeping {cooldown}")
            time.sleep(cooldown)

        player["current_room"] = shape_move_response(r.json(), roomGraph)
        # roomGraph = load_roomgraph()
        roomGraph[f"{player['current_room']['room_id']}"] = player["current_room"]
        save_roomgraph(roomGraph)

        if player["current_room"]["room_id"] == "1":
            break
    sell_everything(key, player, roomGraph)


def sell_everything(key, player, roomGraph):
    print("Selling Everything")
    time.sleep(cooldown)
    r = None
    items = []
    while r is None or len(r.json()["errors"]) > 0:
        print("Getting Status:")
        r = get_status(key)
        rjson = r.json()
        pretty_print(rjson)
        print(f"Sleeping {rjson['cooldown']}")
        time.sleep(rjson["cooldown"])
    items = r.json()["inventory"]
    for i in range(len(items)):
        print(f"Selling: f{items[i]}")
        print(datetime.datetime.now())
        r = sell(key, items[i])
        rjson = r.json()
        pretty_print(rjson)
        print(f"Sleeping {rjson['cooldown']}")
        time.sleep(rjson["cooldown"])
    print("Done.")


def traverse_path(key, player, target_room_id, roomGraph, ignore_weight=None):
    if ignore_weight is None:
        ignore_weight = False
    while True:
        current_id = player["current_room"]["room_id"]
        shortest_route = find_shortest_path(
            current_id, target_room_id, roomGraph, explore_nones=True
        )
        if len(shortest_route) == 0:
            # we're already there
            break
        r = None
        print(f"Shortest Route: {shortest_route}")
        while r is None or len(r.json()["errors"]) > 0:
            print(f"Moving to {shortest_route[0][0]}, {shortest_route[0][1]}")
            r = move(my_key, shortest_route[0][0], shortest_route[0][1])
            this_json = r.json()
            # we moved successfully
            # check for treasure
            print("Good response, Treasure Check")
            if "items" in this_json and not player["max_weight"]:
                pretty_print(this_json)
                while "flower" in this_json["items"]:
                    print(f"flower found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "flower")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False
                while "amazing treasure" in this_json["items"]:
                    print(f"amazing Treasure found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "amazing treasure")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False
                while "great treasure" in this_json["items"]:
                    print(f"great Treasure found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "great treasure")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False
                while "shiny treasure" in this_json["items"]:
                    print(f"Shiny Treasure found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "shiny treasure")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False
                while "small treasure" in this_json["items"]:
                    print(f"Small Treasure found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "small treasure")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if not ignore_weight and "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False

                while "tiny treasure" in this_json["items"]:
                    print(f"Treasure found! {this_json['items']}")
                    print("sleeping cooldown")
                    time.sleep(this_json["cooldown"])
                    pu_response = pickup(my_key, "tiny treasure")
                    # print("Pickup Response:")
                    this_json = pu_response.json()
                    if not ignore_weight and "Item too heavy: +5s CD" in this_json["errors"]:
                        player["max_weight"] = True
                        break
                    else:
                        player["max_weight"] = False
                    # breakpoint()

            rjson = r.json()
            cooldown = rjson["cooldown"]
            print(f"Sleeping {cooldown}")
            time.sleep(cooldown)
            cooldown = 0

        player["current_room"] = shape_move_response(r.json(), roomGraph)
        # roomGraph = load_roomgraph()
        roomGraph[f"{player['current_room']['room_id']}"] = player["current_room"]
        save_roomgraph(roomGraph)
        if "Heavily Encumbered: +100% CD" in r.json()["messages"]:
            player["encumbered"] = True
            # break if we're not headed to sell
            if target_room_id != "0":
                break

        if player["current_room"]["room_id"] == target_room_id:
            break


# roomGraph = load_old_data()
# exit()


####### PROGRAM START ########
roomGraph = load_roomgraph()
# breakpoint()
direction_opposites = {"n": "s", "e": "w", "s": "n", "w": "e"}
initial_exits = {}

# initialize the player
r = None
rjson = None

# if the request fails, sleep the cooldown + half a sec and try again
while True:
    r = init(my_key)
    rjson = r.json()
    cooldown = rjson["cooldown"]
    if r.status_code is not 200:
        print(f"Init statuscode not 200, waiting {cooldown}")
        time.sleep(cooldown + 0.5)
    else:
        print(f"Waiting cooldown {cooldown}")
        time.sleep(cooldown + 0.5)
        cooldown = 0
        break

# pretty_print(rjson)
# pretty_print(get_status(my_key).json())
# exit()
player["current_room"] = shape_move_response(rjson, roomGraph)
roomGraph[f"{rjson['room_id']}"] = player["current_room"]
# save_roomgraph(roomGraph)
# traverse_path(my_key, player, "457", roomGraph, True)
# breakpoint()
breakpoint()

# main traversal loop
# 500 rooms

iteration = 0
# elevation hunter, then random
while True:
    if player["max_weight"]:
        # print("top wuh oh")
        # breakpoint()
        traverse_path(my_key, player, '495', roomGraph)
        breakpoint()
        go_sell(my_key, player, roomGraph)
    print("**** BEGIN ELEVATION TRAVERSAL (Press Enter)")
    # input()
    print(json.dumps(player["current_room"], indent=4, sort_keys=True))
    last_room = player["current_room"]
    # count the number of rooms without elevations
    # we might use these as the first objective
    unelevated_rooms = set()
    for k in roomGraph:
        if roomGraph[f"{k}"] is None:
            # might have to do something here
            print(f"roomGraph[{k}] was None!")
            continue

        if "elevation" not in roomGraph[f"{k}"]:
            unelevated_rooms.add(f"{k}")
    print(f"Unelevated Rooms Count: {len( unelevated_rooms )}")

    # if everyone's got an elevation, we've been everywhere
    if len(unelevated_rooms) == 0:
        if player["encumbered"]:
            target_room = "0"
            # move to 1 away from shop
            traverse_path(my_key, player, target_room, roomGraph)
            # move to shope and sell everything
            # print("wuh oh")
            # breakpoint()
            traverse_path(my_key, player, target_room, roomGraph)
            # go_sell(my_key, player, roomGraph)
            breakpoint()
            player["encumbered"] = False
        else:
            target_room = random.choice(list(roomGraph.keys()))
            traverse_path(my_key, player, target_room, roomGraph)
        continue

    # if iteration == 1:
    #     breakpoint()
    iteration += 1

    # find the next closest unexplored room
    # breadth first search until we find a room
    # in the unelevated room set
    visited = set()
    q = Queue()

    # start the queue with our current neighbors
    # q.enqueue(list(player["current_room"]["exits"].keys))
    for k, v in player["current_room"]["exits"].items():
        # queue an initial path list with this first move
        q.enqueue([(f"{k}", v)])

    # while our queue length is > 0, seek first room without elevation
    while q.size() > 0:

        # dequeue the first path
        path = q.dequeue()

        # the tuple to inspect will be the last one
        t = path[-1]
        room_id = f"{t[1]}"
        room_direction = t[0]

        if len(visited) == len(roomGraph):
            print("Broke on visited condition!")
            break

        # if we haven't checked this room for elevation
        if room_id not in visited:

            # mark it as visited
            visited.add(room_id)

            # if this room doesn't have an elevation
            # we've found the next room to go to
            # BFS is over
            unelevated = None
            # try:
            if room_id is "None" or "elevation" not in roomGraph[room_id]:
                print(f"Next Room: ({room_direction},{room_id})")
                # BFS over
                unelevated = room_id
            else:
                # BFS not over, keep queuing
                # queue all this room's neighbors
                for k, v in roomGraph[room_id]["exits"].items():
                    path_copy = list(path)
                    path_copy.append((k, v))
                    q.enqueue(path_copy)
            # except:
            #     breakpoint()

            if unelevated is not None:
                # we need to go here
                print(
                    f"***** Next Room Objective:  ({room_direction}, {unelevated}) *****"
                )

                # append the tuple from above
                for tt in path:
                    print(f"Move {tt}")
                    this_response = None
                    # until we get a good request through, loop and sleep the cooldowns
                    while True:
                        time.sleep(cooldown)
                        this_response = move(my_key, tt[0], tt[1])
                        if this_response.status_code is not 200:
                            if this_response.status_code == 500:
                                breakpoint()
                                print("500 server status! in move loop")
                                exit()
                            cooldown = this_response.json()["cooldown"]
                            time.sleep(cooldown)
                            cooldown = 0
                            print("Weird Response")
                            # breakpoint()
                            continue
                        else:
                            this_json = this_response.json()
                            # we moved successfully
                            # check for treasure
                            print("Good response, Treasure Check")
                            if "items" in this_json and not player["max_weight"]:
                                while "flower" in this_json["items"]:
                                    print(f"flower found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "flower")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False
                                while "amazing treasure" in this_json["items"]:
                                    print(f"amazing Treasure found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "amazing treasure")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False
                                while "great treasure" in this_json["items"]:
                                    print(f"great Treasure found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "great treasure")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False

                                while "shiny treasure" in this_json["items"]:
                                    print(f"Shiny Treasure found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "shiny treasure")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False

                                while "small treasure" in this_json["items"]:
                                    print(f"Small Treasure found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "small treasure")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False

                                while "tiny treasure" in this_json["items"]:
                                    print(f"Treasure found! {this_json['items']}")
                                    print("sleeping cooldown")
                                    time.sleep(this_json["cooldown"])
                                    pu_response = pickup(my_key, "tiny treasure")
                                    # print("Pickup Response:")
                                    this_json = pu_response.json()
                                    if "Item too heavy: +5s CD" in this_json["errors"]:
                                        player["max_weight"] = True
                                        break
                                    else:
                                        player["max_weight"] = False
                                    # breakpoint()

                            print(json.dumps(this_json, indent=4, sort_keys=True))
                            print(f"Waiting {this_json['cooldown']}")
                            time.sleep(this_json["cooldown"] + 0.5)
                            cooldown = 0
                            # break outta request loop
                            break

                    if (
                        "Heavily Encumbered: +100% CD"
                        in this_response.json()["messages"]
                    ):
                        player["encumbered"] = True

                    player["current_room"] = shape_move_response(
                        this_response.json(), roomGraph
                    )
                    # roomGraph = load_roomgraph()
                    roomGraph[f"{player['current_room']['room_id']}"] = player[
                        "current_room"
                    ]
                    # save_roomgraph(roomGraph)
                print("====EXITING THIS TRAVERSAL====")
                # break out of traversal loop, we've entered a new unelevated room
                break
