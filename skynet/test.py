from treasure_hunter import TreasureHunter
from our_api import OurApi
from treasure_api import LambdaApi
import requests
import json
import time
import os
import sys
import random
import datetime
from decouple import config

import signal
import pdb


# Drop into pdb on ctrl-c so we can issue specific commands
def signal_handler(signal, frame):
    pdb.set_trace()


signal.signal(signal.SIGINT, signal_handler)

##### SETTING UP #####
backend_token = config("BACKEND_TOKEN")
backend_headers = {"content-type": "application/json", "Authorization": backend_token}
url = config("TREASURE_HUNT_URL")
backend_url = config("BACKEND_URL")
name_mappings = None
treasure_hierarchy = [
    "great treasure",
    "shiny treasure",
    "small treasure",
    "tiny treasure",
]

with open("name_mappings.json", "r") as f:
    name_mappings = json.load(f)

lambda_key = ""
if os.path.isfile("key.txt"):
    with open("key.txt", "r") as infile:
        lambda_key = infile.readlines()[0].strip()

if len(sys.argv) >= 2:
    lambda_key = sys.argv[1].strip()

my_name = name_mappings[lambda_key]
print(f"My Name is {my_name}")
if len(lambda_key) == 0 or len(my_name) == 0:
    print("no key or matching name for that key!")
    exit()

headers = {"content-type": "application/json", "Authorization": f"Token {lambda_key}"}

our_api = OurApi(backend_token, backend_url)
lambda_api = LambdaApi(lambda_key, url)
th = TreasureHunter(my_name, our_api, lambda_api)
breakpoint()

