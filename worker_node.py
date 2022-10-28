from dataclasses import asdict, dataclass
import socketio
import time
import random
from energy_status import EnergyStatus
from main_node import energy_status

from monte_carlo_status import MonteCarloStatus


sio = socketio.Client()

SERVER_URL = "http://localhost:8080"
DEBUG = True


is_active = False
compute_result = MonteCarloStatus(0, 0)


@sio.on("compute_on")
def on_message(data):
    compute_result = MonteCarloStatus(data.count_in, data.count_out)
    is_active = True


@sio.on("compute_off")
def on_message(data):
    is_active = False
    send_result(compute_result)


@sio.on("get_result")
def on_message():
    send_result(compute_result)


def send_result(result: MonteCarloStatus):
    sio.emit("result", result.toJson())


@sio.on("*")
def catch_all(event, data):
    print("Received non-standard event")


sio.connect(SERVER_URL)
print("my sid is", sio.sid)


def monte_carlo_step(status: MonteCarloStatus):
    rand_x = random.uniform(-1, 1)
    rand_y = random.uniform(-1, 1)

    origin_dist = rand_x**2 + rand_y**2

    # Checking if (x, y) lies inside the circle
    if origin_dist <= 1:
        status.count_in += 1

    status.count_out += 1

    if DEBUG:
        print(f"Current Approx: {4 * status.count_in / status.count_out}")

    return status


current_monte_carlos_status = MonteCarloStatus(0, 0)
current_energy_status = EnergyStatus(0, 100, 100)

while True:
    current_energy_status.light = random.random()
    sio.emit("energy_status", current_energy_status.as_json())
    if is_active:
        monte_carlo_step(current_monte_carlos_status)
    time.sleep(5)
