"""
Worker main contain the worker main class.
"""
import threading
import time
import requests
import logging
import copy

from settings import DATASTORE_APP_ADDRESS, WORKER_API
from modules.worker.sql_connector import WorkerSqlConnector
from modules.worker.measurements import get_response_ping
from modules.common import get_granularity, build_url
from modules.common import ms_time, ms_sleep
from fastapi.security import APIKeyHeader, APIKeyQuery
import json
from settings import worker_log_config

class Worker():
    """
    Worker class
    """
    #TODO: Kdyz neni dostupny datastore, vyhazuje chybu, mozno testovat tak, ze se zmeni sync-worker na neco jineho

    def __init__(self, run=True):
        logging.config.dictConfig(worker_log_config)
        self.name = "gfdafdsafdsa"# TODO where it should be stored? Should default value be UUID?
        self.datastore_url = build_url(*DATASTORE_APP_ADDRESS, "sync-worker")
        self.sql_conn = WorkerSqlConnector(self.name)
        self.sql_conn.reset_tasks()
        if run:
            self.__run()

    def __io_loop(self):
        """Filling up the storing queue with the data."""
        while True:
            responses = self.sql_conn.presync()
            host_availability = self.sql_conn.presyncHosts()
            payload = {
                "worker": self.name,
                "responses": responses,
                "hosts_availability": host_availability,
                "api": WORKER_API,
            }
            try:
                requests.packages.urllib3.disable_warnings() #later it needs to be removed
                tasks = requests.post(self.datastore_url, json=payload,verify=False).json() #Attention: verify:False
                if tasks is not None:
                    self.sql_conn.postsync(tasks, responses, host_availability)
            except requests.exceptions.RequestException as e:
                logging.critical("Cannot contact datastore - {}".format(str(e)))
                self.sql_conn.postsync([], [], [])
            time.sleep(3)

    def __execute_task(self, task):
        """Start execution thread
        """
        threading.Thread(target=self.__task_thread, args=(task,), daemon=True).start()

    def __task_thread(self, task):
        """Execute task in thread.

        If task was already executed in past, wait time is calculated
        to trigger task at correct time.
        """
        now = ms_time()
        if task["next_run"]:
            wait_time = task["next_run"] - now
            #TODO opakuje se volani, viz komment
            #print("nextRun: " +  str(task["next_run"]) + " rozdil: " + str(wait_time))
            if(wait_time < 0):
                wait_time = 0
        else:
            wait_time = 0

        task["last_run"] = now + wait_time
        task["next_run"] = task["last_run"] + get_granularity(task["frequency"])
        self.sql_conn.update_task(task)
        ms_sleep(wait_time)
        if task["task"] == "ping":
            response = get_response_ping(task["address"], task["timeout"])
            
            #nastavim status available, bud je nedostupny, nebo nesplnuje treshold
            if response != -1 and response < task["treshold"]:
                task["available"] = True
            else:
                task["available"] = False

            task["value"] = response
            #self.__availability(task, response)
        else:
            logging.warning("Unknown task type: {}".format(task["task"]))
            return
        task["time"] = task["last_run"]
        retryCykle = self.sql_conn.add_response(task)
        
        if retryCykle:
            task["next_run"] = task["last_run"] + task["retry_time"]
        self.sql_conn.update_task(task)
        ms_sleep(100)

    def __availability(self, task, response):
        self.sql_conn.createAvailable(task, response)


    def __run(self):
        """
        Main loop of the worker class.

        Task thread is started earlier to allow waiting on exact time in the thread.
        """
        threading.Thread(target=self.__io_loop, daemon=True).start()
        logging.info("Worker started.")

        ## Check hostStatus
        self.sql_conn.initTasks()

        while True:
            tasks = self.sql_conn.get_tasks()
            now = ms_time()
            for task in tasks:
                if task["last_run"] == 0:
                    self.__execute_task(copy.deepcopy(task))
                elif (task["next_run"] - ms_time(2)) < now:
                    self.__execute_task(copy.deepcopy(task))
            ms_sleep(500)
