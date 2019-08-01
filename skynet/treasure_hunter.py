# from .our_api import OurApi
# from .treasure_api import LambdaApi

treasure_hierarchy = [
    "great treasure",
    "shiny treasure",
    "small treasure",
    "tiny treasure",
]

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
    def __init__(
        self,
        name=None,
        our_api=None,
        lambda_api=None,
    ):
        self.inventory = []
        self.weight = None
        self.our_api = our_api
        self.lambda_api = lambda_api

    def refresh_rooms(self):
        return self.our_api.get_rooms()
