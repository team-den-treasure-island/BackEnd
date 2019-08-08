import hashlib
import requests
import sys
import time
import random
from treasure_api import TreasureApi
from decouple import config

# TODO: Implement functionality to search for a proof


def proof_of_work(last_proof, difficulty):
    proof = random.randint(0, 1000000)
    while valid_proof(last_proof, proof, difficulty) is False:
        proof += 1
    print("Proof found: " + str(proof))
    return proof


def valid_proof(last_proof, proof, difficulty):
    guess = f"{last_proof}{proof}".encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return guess_hash[:difficulty] == "0" * difficulty


if __name__ == "__main__":
    # What node are we interacting with?
    # if len(sys.argv) > 1:
    #     node = sys.argv[1]
    # else:
    # node = "https://lambda-treasure-hunt.herokuapp.com/api/bc"
    node = config("TREASURE_HUNT_URL")
    treasure_api = TreasureApi(sys.argv[1].strip(), node)
    print(treasure_api.mine_url)
    print(node)
    coins_mined = 0
    # Run forever until interrupted
    while True:
        # TODO: Get the last proof from the server and look for a new one
        # headers = {
        #     "content-type": "application/json",
        #     "Authorization": f"Token {sys.argv[1]}",
        # }
        # r = requests.get(f"{node}/last_proof", headers=headers)
        # data = r.json()

        data = None
        # while True:
        #     data = treasure_api.last_proof()
        #     if data.get("difficulty") < 7:
        #         break
        data = treasure_api.last_proof()

        last_proof = data["proof"]
        print(data)
        new_proof = proof_of_work(last_proof, data["difficulty"])

        # TODO: When found, POST it to the server {"proof": new_proof}
        # post_data = {"proof": new_proof}
        # r = requests.post(f"{node}/mine", json=post_data, headers=headers)
        data = treasure_api.mine(new_proof)
        print(data)
        # exit()
        # print(data)
        # time.sleep(90)
        # # TODO: If the server responds with 'New Block Forged'
        if "New Block Forged" in data.get("messages"):
            #     # add 1 to the number of coins mined and print it.  Otherwise,
            coins_mined += 1
            #     # print the message from the server.
            print("Total coins mined: ", coins_mined)
        else:
            print(data.get("messages"))
