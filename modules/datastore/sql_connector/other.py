"""
takes care of the connection to the database
"""
from sqlalchemy.sql import func, exists
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker,joinedload
import sqlite3 #  i have added this if you find better way to handle databases, you can remove it

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task, HostStatus
from modules.datastore.models import make_tables
from modules.sql_connector import CommonSqlConnector
from modules.datastore.data_validation import DataValidation
import json

class SqlOther(CommonSqlConnector):
    """
    Extra sql operations required for Datastore.
    """

    def __init__(self, db_connection):
        self.sessions = db_connection

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()
            session.query(Address).delete()
    def sync_worker(self, data):
        """
        Sync worker - store responses and return tasks
        """
        worker_id = self.get_worker(data.api)
        if worker_id is not None:
            with self.sessions.begin() as session:
                if data.responses is not None:
                    for response in data.responses:
                        result = Response(
                            address=response.address,
                            time=response.time,
                            value=response.value,
                            task=response.task,
                            worker=worker_id
                        )
                        session.add(result)
                if data.hosts_availability is not None:
                    for host in data.hosts_availability:
                        result = HostStatus(
                            address=host.address,
                            time_from=host.time_from,
                            time_to=host.time_to,
                            available=host.available,
                            worker_id=worker_id
                        )
                        session.add(result)
                    # TODO alter task last update

                tasks = session.query(Task).join(Task, Worker.task).filter(Worker.id == worker_id).join(Address, Task.address_id == Address.id)


                # TODO: predelat aby byl vystupni model definovam v models.py
                results = [
                    {
                        'id': task.id,
                        'task': task.task,
                        'running': task.running,
                        'last_run': task.last_run,
                        'hide': task.hide,
                        'frequency': task.frequency,
                        'address': task.address.address,
                        'timeout': task.timeout,
                        'treshold': task.treshold,
                        'retry': task.retry,
                        'retry_time': task.retry_time
                    }
                    for task in tasks
                ]
                return results

#                return [item.__dict__ for item in tasks.all()] # TODO make custom function in Task class (instead of __dict__)

    def get_worker(self, token):
        try:
            with self.sessions.begin() as session:
                result = session.query(Worker).filter(Worker.token == token).one()
                return result.id
        except:
            return None

    def get_workers(self):
        try:
            with self.sessions.begin() as session:
                result = session.query(Worker)
                return [item.__dict__ for item in result.all()]
        except:
            return None

    def create_worker(self, worker_name, api_key):
        """
        add new task
        """ # TODO add colors and name to database
        test = DataValidation()
        result = Worker(
            name=worker_name,
            token=api_key
        )

        with self.sessions.begin() as session:
            session.add(result)

        return {"status": "200"}
    