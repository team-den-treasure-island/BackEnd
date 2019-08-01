### LAMBDA BACKEND
class LambdaApi:
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

    def dash(self, direction, rooms):
        res = requests.post(
            f"{ url }/change_name",
            json={
                "direction": direction,
                "num_rooms": len(rooms),
                "next_room_ids": ",".join(rooms),
            },
            headers=headers,
        )
        return handle_res(res)

    def change_name(self, name):
        res = requests.post(
            f"{ url }/change_name",
            json={"name": name, "confirm": "aye"},
            headers=headers,
        )
        return handle_res(res)

    def pp(self, ugly_json):
        print(json.dumps(ugly_json, indent=4, sort_keys=True))

    def init(self):
        res = requests.get(f"{ url }/init", headers=headers)
        return handle_res(res)

    def move(self, direction, next_room):
        res = requests.post(
            f"{ url }/move",
            json={"direction": direction, "next_room_id": str(next_room)},
            headers=headers,
        )
        update_player(my_name, res.json())
        return handle_res(res)

    def pray(self):
        res = requests.post(f"{ url }/pray", data={}, headers=headers)
        return handle_res(res)

    def flight(self, direction):
        res = requests.post(
            f"{ url }/pray", json={"direction": direction}, headers=headers
        )
        return handle_res(res)

    def dash(self, direction, num_rooms, next_room_ids):
        res = requests.post(
            f"{ url }/pray",
            json={
                "direction": direction,
                "num_rooms": num_rooms,
                "next_room_ids": ",".join(next_room_ids),
            },
            headers=headers,
        )
        return handle_res(res)

    def sell(self, name):
        res = requests.post(
            f"{ url }/sell", json={"name": name, "confirm": "yes"}, headers=headers
        )
        return handle_res(res)

    def pickup(self, name):
        res = requests.post(f"{ url }/take", json={"name": name}, headers=headers)
        return handle_res(res)

    def get_status(self):
        res = requests.post(f"{ url }/status", data={}, headers=headers)
        return handle_res(res)

    def get_balance(self):
        res = requests.get(f"{ url }/bc/get_balance", headers=headers)
        return handle_res(res)

    def mine(self, proof):
        res = requests.get(f"{ url }/bc/mine", json={"proof": proof}, headers=headers)
        return handle_res(res)

    def transmogrify(self, name):
        res = requests.post(
            f"{ url }/transmogrify", json={"name": name}, headers=headers
        )
        return handle_res(res)
