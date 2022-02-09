"""Main

This script has the main loop where the tasks are executed by a new thread and
the results are queued in a specific thread.

This tool accepts any kind of task, address and time(freq or daytime) provided
in the config.

This script requires that `ping3` and `datetime` be installed within the Python
environment you are running this script in.

"""

import threading, queue
from datetime import datetime
import time
import json
import copy

import ping3

from storages.engines import get_writer_engine


def ping(address):
    """Convert None values to -1 and 0.0 values to 0.016."""
    result = ping3.ping(address)

    if type(result) == float:
        if result == 0.0:
            return 0.016
        else:
            return result
    else:
        return -1

def get_granularity(granularity):
    """Convert frequencies to seconds."""
    FREQS = {
        "H": 60 * 60,
        "M": 60,
        "S": 1,
        "D": 24 * 60 * 60,
    }
    number, letter = int(granularity[:-1]), granularity[-1]
    return number * FREQS[letter]


def execute_task(task):
    """Assign a new thread to the new task."""
    task["last_run"] = time.time()
    task["next_run"] = time.time() + get_granularity("1D") - 60 # security buffer
    threading.Thread(target=execute_thread, args=(task["type"], task["address"]), daemon=True).start()


def execute_thread(task_type, address):
    """Execute task by thread.
    Keyword arguments:
    task_type -- the type of task (currently only ping)
    address -- the url or IP address
    """
    if task_type == "ping":
        response = {
            "type": task_type,
            "address": address,
            "time": int(time.time()),
            "value": ping(task["address"])
        }
    else:
        # TODO: add any other task_type ex.(trace route, http requests, etc)
        pass
    response_queue.put(response)


def writer_loop(settings):
    """Filling up the storing queue with the data."""
    storage_engine = get_writer_engine(settings["engine"])
    while True:
        while not response_queue.empty():
            response = response_queue.get()
# writing the response based on the storage_engine
            storage_engine.write(response)
            response_queue.task_done()
            time.sleep(0.001)
        time.sleep(settings["sleep"])


response_queue = queue.Queue() # the response queue is the thread queue

with open("config.json", "r") as f:
    config = json.loads(f.read())
tasks = config["tasks"]



# Result queue thread
threading.Thread(target=writer_loop, args=[copy.copy(config["writer_settings"])], daemon=True).start()


while True:
    now = datetime.now()
    current_time = now.strftime("%H:%M")

    """Separating the frequencies and the daytime tasks."""
    for task in tasks:
        # logic for frequency based tasks
        if "freq" in task.keys():
            if not "last_run" in task.keys(): # starting from scratch
                execute_task(task)
            else:
                if time.time() > get_granularity(task["freq"]) + task["last_run"]:
                    execute_task(task)
        # logic for daytime based tasks
        elif "daytime" in task.keys():
            if not "next_run" in task.keys() and current_time == task["daytime"]:

                execute_task(task)
            elif "next_run" in task.keys():
                if time.time() >= task["next_run"] and current_time == task["daytime"]:
                    execute_task(task)
         # if no information known?
        else:
            error = {
                "type": task["type"],
                "address": task["address"],
                "value": "Error"
            }

    time.sleep(0.3)