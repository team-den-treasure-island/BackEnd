import requests

##### class for our api requests
class OurApi:
    def __init__(self, token=None, url=None):
        self.token = token
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Token {token}",
        }
        self.url = url

    def handle_res(self, res):
        try:
            return res.json()
        except Exception as e:
            return {"error": res.content}

    def get_rooms(self):
        res = requests.get(f"{self.url}rooms/")
        return self.handle_res(res)

    # update or create room if not exists
    def update_room(self, room_id, room_data):
        res = requests.put(
            f"{self.url}rooms/{room_id}/", json=room_data, headers=self.headers
        )
        if res.status_code == 404:
            create_player(room_data)
        return self.handle_res(res)

    def create_room(self, room_data):
        res = requests.post(
            f"{self.url}rooms/{room_id}/", json=room_data, headers=self.headers
        )
        return self.handle_res(res)

    def create_player(self, name, move_data):
        res = requests.post(
            f"{ self.url }players/",
            json={
                "name": name,
                "current_room": move_data["room_id"],
                "cooldown": move_data["cooldown"],
            },
            headers=self.headers,
        )
        return self.handle_res(res)

    def update_player(self, name, move_data):
        res = requests.put(
            f"{ self.url }players/{name}/",
            json={
                "name": name,
                "current_room": move_data["room_id"],
                "cooldown": move_data["cooldown"],
            },
            headers=self.headers,
        )
        if res.status_code == 404:
            create_player(name, move_data)
        return self.handle_res(res)
