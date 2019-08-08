import requests
import json
import time
import os
import sys
import random
import datetime
from decouple import config
import asyncio
import websockets

import signal
import pdb

url = config('BACKEND_WS_URL')
is_alive = True


async def alive():
    while is_alive:
        print('Alive')
        await asyncio.sleep(300)


async def async_processing():
    async with websockets.connect(f'{url}/updates/') as websocket:
        while True:
            try:
                # await websocket.send("Test Client")
                message = await websocket.recv()
                print(message)

            except websockets.exceptions.ConnectionClosed:
                print('ConnectionClosed')
                is_alive = False
                break


tasks = [
    asyncio.ensure_future(alive()),
    asyncio.ensure_future(async_processing())
]
asyncio.get_event_loop().run_until_complete(asyncio.wait(tasks))
# asyncio.get_event_loop().run_until_complete(alive())
# asyncio.get_event_loop().run_until_complete(async_processing())
