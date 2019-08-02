# from .our_api import OurApi
# from .treasure_api import LambdaApi

TREASURE_HIERARCHY = [
    "great treasure",
    "shiny treasure",
    "small treasure",
    "tiny treasure",
]
DIRECTION_OPPOSITES = {"n": "s", "e": "w", "s": "n", "w": "e"}
DIRECTIONS = ["n", "s", "e", "w"]


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

    # update our roomGraph
    def refresh_rooms(self):
        res = self.our_api.get_rooms()
        for room in res:
            # manipulate our api's room data response to match
            # lambda's
            room["exits"] = {
                d: room[f"{d}_to"]
                for d in DIRECTIONS
                if room.get(f"{d}_to") is not None
            }
            self.roomGraph[f"{room['room_id']}"] = room
        return res

    # update from our api
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

    # update from lambda api
    def prepare_to_start(self):
        self.refresh_our_info()
        if self.explore_mode == True:
            # we're not ready to go
            # someone turned us off
            return False

        lambda_info = self.lambda_api.init()
        # breakpoint()
        if lambda_info.get("error") is not None:
            print(lambda_info.get("error"))
            return
        self.room_id = lambda_info.get("room_id")

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
                    all_paths.append( path )

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
