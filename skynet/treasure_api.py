import requests
import json
import time

### LAMBDA BACKEND
class LambdaApi:
    def __init__(self, token=None, url=None):
        self.token = token
        self.headers = {
            "content-type": "application/json",
            "Authorization": f"Token {token}",
        }
        self.url = url
        self.cooldown = 0
        self.last_action = time.time()
        self.retries = 2  # number of retries

    # HOF to call function awaiting the cooldown
    def cooldown_request(self, f, *args, **kwargs):
        attempts = 0
        while attempts < self.retries:
            try:
                elapsed = time.time() - self.last_action
                if self.cooldown > elapsed:
                    sleep_time = self.cooldown - elapsed
                    print(f"Awaiting Cooldown: {sleep_time}")
                    time.sleep(sleep_time)
                    self.cooldown = 0
                response = self.handle_res(f(*args, **kwargs))
                if response.get("cooldown"):
                    self.cooldown = response.get("cooldown")
                self.last_action = time.time()

                if response.get("errors"):
                    raise ValueError("Cooldown Request Failure", response)
                break
            except ValueError as err:
                attempts += 1
                print(err)
        return response

    # manage all cooldowns from requests here
    def handle_res(self, res):
        try:
            rjson = res.json()
            return rjson
        except Exception as e:
            return {"errors": [res.content]}

    def dash(self, direction, rooms):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/change_name",
            json={
                "direction": direction,
                "num_rooms": len(rooms),
                "next_room_ids": ",".join(rooms),
            },
            headers=self.headers,
        )

    def change_name(self, name):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/change_name",
            json={"name": name, "confirm": "aye"},
            headers=self.headers,
        )

    def pp(self, ugly_json):
        print(json.dumps(ugly_json, indent=4, sort_keys=True))

    def init(self):
        return self.cooldown_request(
            requests.get, f"{ self.url }/init", headers=self.headers
        )

    def move(self, direction, next_room):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/move",
            json={"direction": direction, "next_room_id": str(next_room)},
            headers=self.headers,
        )

    def fly(self, direction, next_room):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/fly",
            json={"direction": direction, "next_room_id": str(next_room)},
            headers=self.headers,
        )


    def pray(self):
        return self.cooldown_request(
            requests.post, f"{ self.url }/pray", data={}, headers=self.headers
        )

    def flight(self, direction):
        return requests.post(
            f"{ self.url }/pray", json={"direction": direction}, headers=self.headers
        )

    def dash(self, dash_path):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/pray",
            json={
                "direction": dash_path[0][0],
                "num_rooms": len(dash_path),
                "next_room_ids": ",".join(dash_path),
            },
            headers=self.headers,
        )

    def sell(self, name):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/sell",
            json={"name": name, "confirm": "yes"},
            headers=self.headers,
        )

    def pickup(self, name):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/take",
            json={"name": name},
            headers=self.headers,
        )

    def get_status(self):
        return self.cooldown_request(
            requests.post, f"{ self.url }/status", data={}, headers=self.headers
        )

    def get_balance(self):
        return self.cooldown_request(
            requests.get, f"{ self.url }/bc/get_balance/", headers=self.headers
        )

    def mine(self, proof):
        return self.cooldown_request(
            requests.get,
            f"{ self.url }/bc/mine",
            json={"proof": proof},
            headers=self.headers,
        )

    def transmogrify(self, name):
        return self.cooldown_request(
            requests.post,
            f"{ self.url }/transmogrify",
            json={"name": name},
            headers=self.headers,
        )
