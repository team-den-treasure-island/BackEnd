# from .our_api import OurApi
# from .treasure_api import LambdaApi
import sys
import time

TREASURE_HIERARCHY = [
    "great treasure",
    "shiny treasure",
    "small treasure",
    "tiny treasure",
]
DIRECTION_OPPOSITES = {"n": "s", "e": "w", "s": "n", "w": "e"}
DIRECTIONS = ["n", "s", "e", "w"]
ITEM_WEIGHTS = {"shiny treasure": 2}


class Stack:
    def __init__(self):
        self.stack = []

    def push(self, value):
        self.stack.append(value)

    def pop(self):
        if self.size() > 0:
            return self.stack.pop()
        else:
            return None

    def size(self):
        return len(self.stack)


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


class TreasureHunter:
    def __init__(self, name=None, our_api=None, lambda_api=None):
        self.inventory = []
        self.weight = None
        self.our_api = our_api
        self.lambda_api = lambda_api
        self.roomGraph = {}
        # if this is true, we're paused for user actions
        # assume it's true to start, so bot doesn't do anything
        self.explore_mode = True
        self.players = []
        self.name = name
        self.room_id = None
        self.destination = None
        self.can_fly = False
        self.can_dash = False
        self.inventory = []
        self.gold = 0
        self.encumberance = 0
        self.strength = 0
        self.movement_queue = []
        self.tick = 0
        self.tick_time = 500
        self.titleToId = {}
        self.pickup_mode = False

    # update our roomGraph
    def refresh_rooms(self):
        res = self.our_api.get_rooms()
        for room in res:
            # manipulate our api's room data response to match
            # lambda's
            self.titleToId[room.get("title")] = room.get("room_id")
            room["exits"] = {
                d: room[f"{d}_to"]
                for d in DIRECTIONS
                if room.get(f"{d}_to") is not None
            }
            self.roomGraph[f"{room['room_id']}"] = room
        return res

    # update position and explore_mode from our api
    def refresh_our_info(self):
        res = self.our_api.get_players()
        # breakpoint()
        for player in res:
            if self.name == player["name"]:
                self.explore_mode = player.get("explore_mode")
                break
        self.players = res
        for player in res:
            if player.get("name") == self.name:
                self.room_id = player.get("current_room")
                self.explore_mode = player.get("explore_mode")
        return res

    # refresh my lambda status
    def update_status(self):
        # unsafe here but going with it for now
        status = self.lambda_api.get_status()
        self.encumberance = status.get("encumberance")
        self.strength = status.get("strength")
        self.inventory = status.get("inventory")
        self.room_id = status.get("room_id")

        # if we have one item, we know the weight off our encumberance
        # opportunity to store weights on backend
        if self.inventory is not None and len(self.inventory) == 1:
            TREASURE_WEIGHTS[self.inventory[0]] = self.encumberance
        self.gold = status.get("gold")

    # update from lambda api
    def prepare_to_start(self):
        self.refresh_our_info()
        if self.explore_mode == True:
            # we're not ready to go
            # someone turned us off
            return False
        self.update_status()

    # find all paths and estimate their time based on
    # ability use, elevation, and traps
    def find_shortest_path_by_time(self, start_id, end_id):
        all_paths = self.find_all_paths(start_id, end_id)

        lowest_time = sys.maxsize
        lowest_path = None

        # iterate over all paths
        for path in all_paths:
            time_factor = 0
            reduced_path = list(path)

            # if we can dash, consider the dash lines as one step
            if self.can_dash:
                i = 0
                while i < len(path) - 1:
                    count_repeats = 1
                    j = i
                    while j < len(path) - 1:
                        if path[j][0] != path[j + 1][0]:
                            break
                        count_repeats += 1
                        j += 1
                    if count_repeats > 2:
                        i += count_repeats
                        time_factor += 33
                        reduced_path = path[count_repeats:]
                    elif (
                        count_repeats == 2
                        and self.roomGraph[str(path[i][1])].get("terrain") == "TRAP"
                    ):
                        # we're inefficiently going to jump the traps
                        time_factor += 33
                        reduced_path = path[count_repeats:]
                    else:
                        # otherwise, we're moving to each
                        time_factor += 15
                        i += 1

            if self.can_fly:
                # if you can fly, you skip a bit of cooldown
                for move in reduced_path:
                    if self.roomGraph[str(move[1])].get("elevation") > 0:
                        time_factor -= 5

            for move in reduced_path:
                # add trap penalties
                if self.roomGraph[str(move[1])].get("terrain") == "TRAP":
                    time_factor += 30

            if time_factor < lowest_time:
                lowest_time = time_factor
                lowest_path = path
        return lowest_path

    # bfs to find the shortest route by number of rooms
    def find_shortest_path(self, start_id, end_id):
        # we're already there!
        if start_id == end_id:
            return []

        current_room = self.roomGraph[start_id]
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

                # if we found the path, return it
                if room_id == end_id:
                    return path

                if len(visited) == len(self.roomGraph):
                    print("Ran out of rooms trying to find path!")
                    exit()

                if room_id not in visited:
                    # add it
                    visited.add(room_id)
                    # queue up neighbors
                    if room_id in self.roomGraph:
                        for k, v in self.roomGraph[room_id]["exits"].items():
                            path_copy = list(path)
                            path_copy.append((k, v))
                            q.enqueue(path_copy)

    # bfs until we've gone through all rooms and
    # collected all paths between these 2 ids
    def find_all_paths(self, start_id, end_id):
        # we're already there!
        if start_id == end_id:
            return []

        current_room = self.roomGraph[start_id]
        all_paths = []
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

                # if we found the path, return it
                if room_id == end_id:
                    all_paths.append(path)

                if len(visited) == len(self.roomGraph):
                    # break out condition
                    return all_paths

                if room_id not in visited:
                    # add it
                    visited.add(room_id)
                    # queue up neighbors
                    if room_id in self.roomGraph:
                        for k, v in self.roomGraph[room_id]["exits"].items():
                            path_copy = list(path)
                            path_copy.append((k, v))
                            q.enqueue(path_copy)

    # Brain Function
    def brain_tick():
        elapsed = time.time() - self.tick
        self.tick = time.time()

        self.refresh_our_info()

        # check explore mode
        if self.explore_mode:
            time.sleep(120)
            return

        # if it's still on, assume control
        elif self.explore_mode:
            self.our_api.update_player(self.name, {"explore_mode": False})
            self.explorer_mode = False

        # update from lambda, rate limiter is on the API
        self.update_status()
        overweight = self.encumberance > self.strength
        max_weight = self.encumberance >= 19

        # if we don't know where the shop is
        if self.titleToId.get("Shop") is None:
            # do something cool!
            print("No Shop!")
            pass

        if self.titleToId.get("Pirate Ry's") is None:
            # do something cool!
            print("No Pirate!")
            pass

        if self.titleToId.get("Linh's Shrine") is None:
            # do something cool!
            print("No Dash Shrine!")
            pass

        if self.titleToId.get("The Peak of Mt. Holloway") is None:
            # do something cool!
            print("No Flight Shrine!")
            pass

        # if we're max weight, go home on the double
        if max_weight:
            self.pickup_mode = False
            self.go_sell(self.pickup_mode)
            pass

        # if we're overweight, I mean... treasure's treasure
        if overweight:
            self.pickup_mode = True
            # self.go_sell(False)
            pass

        if not self.can_dash:
            # go to the dash shrine fast
            self.pickup_mode = False
            self.go_to_id(this.nameToId("Linh's Shrine"))
            self.lambda_api.pray()
            self.can_dash = True
            self.our_api.update_player(self.name, {"can_dash": True})
            pass

        if not self.can_fly:
            # go to the fly shrine fast
            self.pickup_mode = False
            self.go_to_id(this.nameToId("The Peak of Mt. Holloway"))
            self.lambda_api.pray()
            self.can_fly = True
            self.our_api.update_player(self.name, {"can_fly": True})
            pass

        next_route = None
        if self.destination:
            # move to destination
            next_route = find_shortest_path_by_time(self.destination)
        else:
            # otherwise, we're on the hunt!
            choice = None
            roomKeys = list(self.roomGraph.keys())
            while choice is not None and roomGraph[choice].get("terrain") != "TRAP":
                choice = random.choice(roomKeys)
            next_route = find_shortest_path_by_time(
                random.choice(list(self.roomGraph.keys()))
            )

        dash_count = 0
        next_room = next_route[0]

        # while dash_count < 2:

        # check if room after next is the same direction and a trap
        # > 2 here because we might be moving to a trap room
        if (
            len(next_route) > 2
            and next_route[0][0] == next_route[1][0]
            and next_route[1].get("terrain") == "TRAP"
        ):
            # self.dash()
            pass

        # count dashes if possible
