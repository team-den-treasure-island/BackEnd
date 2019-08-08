from channels.generic.websocket import JsonWebsocketConsumer
from asgiref.sync import async_to_sync
import json

# synchronous websocket consumer that accepts all connections
# any messages received will be echoed back to the same
# client
class UpdateConsumer(JsonWebsocketConsumer):
    def connect(self):
        # self.channel_layer.group_add("update", self.channel_name)
        async_to_sync(self.channel_layer.group_add)("update", self.channel_name)
        self.accept()
        print(f"Added {self.channel_name} channel to update")

    def disconnect(self, code):
        self.channel_layer.group_discard("update", self.channel_name)
        print(f"Removed {self.channel_name} channel from update")

    def player_update(self, event):
        # breakpoint()
        self.send_json(event)
        print(f"Got message {event} at {self.channel_name}")

    def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        print(text_data_json)
        message = text_data_json["message"]

        self.send(text_data=json.dumps({"message": message}))
