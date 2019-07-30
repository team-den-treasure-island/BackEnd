import requests
import json
import time
import os
import sys

class Queue():
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

my_key = ""
if os.path.isfile("key.txt"):
    with open("key.txt", "r") as infile:
        my_key = infile.readlines()[0].strip()

if len(sys.argv) >= 2:
    my_key = sys.argv[1].strip()

if len(my_key) == 0:
    print("No key provided!")
    exit()

url = "https://lambda-treasure-hunt.herokuapp.com/api/adv"
headers = {"content-type": "application/json", "Authorization": f"Token {my_key}"}
cooldown = 0

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
    r = requests.post(f"{ url }/move", json={"direction": direction, "next_room_id": str(next_room)}, headers=headers)
    return r

# breakpoint()


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
        "exits": {d: None for d in response["exits"] },
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


roomGraph = load_old_data()
# exit()


####### PROGRAM START ########
roomGraph = load_roomgraph()
player = {}
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

player["current_room"] = shape_move_response(rjson, roomGraph)


roomGraph[f"{rjson['room_id']}"] = player["current_room"]
save_roomgraph(roomGraph)

# main traversal loop
# 500 rooms

iteration = 0
# elevation hunter
while True:
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
    for k,v in player["current_room"]["exits"].items():
        # queue an initial path list with this first move
        q.enqueue([(f"{k}",v)])

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
            if "elevation" not in roomGraph[room_id]:
                # BFS over
                unelevated = room_id
            else:
                # BFS not over, keep queuing
                # queue all this room's neighbors
                path_copy = list(path)
                for k,v in roomGraph[room_id]["exits"].items():
                    path_copy = list(path)
                    path_copy.append((k,v))
                    q.enqueue(path_copy)
            # except:
            #     breakpoint()

            if unelevated is not None:
                # we need to go here
                print(f"***** Next Room Objective:  ({room_direction}, {unelevated}) *****")

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
                            # break outta request loop
                            print(f"Good response!, waiting {this_response.json()['cooldown']}")
                            print(json.dumps(this_response.json(), indent=4, sort_keys=True))
                            time.sleep(this_response.json()["cooldown"])
                            cooldown = 0
                            # breakpoint()
                            break


                    player["current_room"] = shape_move_response(this_response.json(), roomGraph)
                    roomGraph = load_roomgraph()
                    roomGraph[f"{player['current_room']['room_id']}"] = player["current_room"]
                    save_roomgraph(roomGraph)
                print("====EXITING THIS TRAVERSAL====")
                # break out of traversal loop, we've entered a new unelevated room
                break


