"""
Hardcoded settings for the project
"""
import sys
import pathlib
import copy
import os

from modules.common import build_url

## User specified part

TESTING = False

WORKER_API = "9d207bf0-10f5-4d8f-a479-22ff5aeff8d1"
DATABASE_FOLDER = "databases"
LOG_FOLDER = "logs"

DATASTORE_DATABASE_FILE = "datastore.db"
DATASTORE_LOG_NAME = "datastore.log"
DATASTORE_APP_ADDRESS = ("127.0.0.1", 8000)

WORKER_DATABASE_FILE = "worker.db"
WORKER_LOG_NAME = 'worker.log'




## Testing override

if 'unittest' in sys.modules.keys():
    TESTING = True

    DATASTORE_DATABASE_FILE = "datastore_test.db"
    DATASTORE_LOG_NAME = "datastore_test.log"
    DATASTORE_APP_ADDRESS = ("127.0.0.1", 5000)

    WORKER_DATABASE_FILE = "worker_test.db"
    WORKER_LOG_NAME = 'worker_test.log'


## Calculated part

for folder_path in [DATABASE_FOLDER, LOG_FOLDER]:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


DATASTORE_APP_URL = build_url(*DATASTORE_APP_ADDRESS)
DATASTORE_DATABASE = pathlib.PurePath(DATABASE_FOLDER, DATASTORE_DATABASE_FILE)

WORKER_DATABASE = pathlib.PurePath(DATABASE_FOLDER, WORKER_DATABASE_FILE)

LOG_CONFIG_TEMPLATE = {
    "version": 1,
    "root": {
        "handlers": ["console", "file"],
        "level": "DEBUG"
    },
    "handlers": {
        "console": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "level": "DEBUG"
        },
        "file": {
            "formatter": "default",
            "class": "logging.handlers.RotatingFileHandler",
            "filename": "<replace-name>",
            "level": "DEBUG"
        }
    },
    "formatters": {
        "default": {
            "format": "%(asctime)s | %(levelname)s | %(module)s | %(message)s",
            "datefmt": "%Y-%m-%d %I:%M:%S"
        }
    },
}

worker_log_config = copy.deepcopy(LOG_CONFIG_TEMPLATE)
worker_log_config["handlers"]["file"]["filename"] = pathlib.PurePath(LOG_FOLDER, WORKER_LOG_NAME)

datastore_log_config = copy.deepcopy(LOG_CONFIG_TEMPLATE)
datastore_log_config["handlers"]["file"]["filename"] = pathlib.PurePath(LOG_FOLDER, DATASTORE_LOG_NAME)
