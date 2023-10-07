"""
This is the main script that starts everything.

TODO: nice to have feature: export responses from database
TODO: page with statuses of pages that are traced
TODO: response value should be string?
TODO: datastore should have table for server informations (gps, name, etc.)
"""
from multiprocessing import Process
import time

import uvicorn

from modules.worker.main import Worker
from settings import DATASTORE_APP_ADDRESS
from subprocess import Popen

def run_worker_app_process():
    """
    start the worker application as a process
    """
    worker_app_proc = Process(target=Worker)
    worker_app_proc.start()
    return worker_app_proc

def run_storage_app(address, port):
    """
    start the storage application with uvicorn
    """
    #uvicorn.run("modules.datastore.main:app", host=address,
    #           port=port, log_level="debug") # TODO critical log level in production maybe
    #Popen(['python', '-m', 'https_redirect'])
    uvicorn.run("modules.datastore.main:app", port=port, host=address)
#            reload=True, reload_dirs=['html_files'],
#            ssl_keyfile='certificate/Local1Key.pem',
#            ssl_certfile='certificate/Local1crt.pem')


def run_storage_app_process(address, port):
    """
    run storage app as a process
    """
    storage_app_proc = Process(target=run_storage_app, args=(address, port))
    storage_app_proc.start()
    return storage_app_proc


if __name__ == "__main__":
    run_storage_app_process(*DATASTORE_APP_ADDRESS)
    run_worker_app_process()

    while True:
        time.sleep(10)
