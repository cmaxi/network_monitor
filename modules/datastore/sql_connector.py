"""
takes care of the connection to the database
"""
from sqlalchemy.sql import func, exists
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker
import sqlite3 #  i have added this if you find better way to handle databases, you can remove it

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address
from modules.datastore.models import make_tables
from modules.sql_connector import CommonSqlConnector

class DatastoreSqlConnector(CommonSqlConnector):
    """
    Extra sql operations required for Datastore.
    """

    def __init__(self):
        """
        Init the sql connector (connect, prepare tables).
        """
        engine = db.create_engine('sqlite:///{}'.format(DATASTORE_DATABASE), echo=True)
        make_tables(engine)
        self.sessions = sessionmaker(engine)
        
    def get_all_responses(self):
        """
        generate JSON of all responses
        """ # TODO time selection

        with self.sessions.begin() as session:
            query = session.query(Response)
            return {"status": "200", "data": [item.values() for item in query.all()]}
    
    def get_all_responses_from(self, time_from):
    """
    generate JSON of all responses from
    """ # TODO time selection

    with self.sessions.begin() as session:
        query = session.query(Response)
        query = query.filter(Response.time > time_from)
        return {"status": "200", "data": [item.values() for item in query]}

    def create_task(self, data):
        """
        add new task
        """ # TODO add colors and name to database

        result = Task(
            address=data[0],
            frequency=data[2],
            task=data[1],
            worker=data[3]
        )

        with self.sessions.begin() as session:
                    existAddress = session.query(exists().where(Task.address == data[0])).scalar()
                    if not existAddress:
                        session.add(result)

        return {"status": "200"}

    def delete_task(self, address):
        """
        delete address from tasks and responses of address
        """
        with self.sessions.begin() as session:
            addressTask = session.query(Task).filter(Task.address == address).delete()

        return {"status": "200"}
    
    def delete_addr_responses(self, address):
        with self.sessions.begin() as session:
            addressResponses = session.query(Response).filter(Response.address == address).delete()

        return "ok"

    def delete_all_responses(self):
        """
        delete all responses
        """
        with self.sessions.begin() as session:
            session.query(Response).delete()
        return {"status": "200"}

    def update_task(self, data):
        """
        update task (dell old and save new)
        """
        print(data)
        result = Task(
            address=data[0],
            frequency=data[2],
            task=data[1],
            worker=data[3]
        )

        with self.sessions.begin() as session:
                    addressTask = session.query(Task).filter(Task.address == data[4]).delete()
                    existAddress = session.query(exists().where(Task.address == data[4])).scalar()
                    if not existAddress:
                        session.add(result)

        return {"status": "200"}

    def pause_task(self, data):
        """
        pause task just remove task from list
        """
        if data[4]=='false':
            self.delete_task(data[0])

        else:
            self.create_task(data)

        return {"status": "200"}

    def get_worker_tasks(self, worker):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).filter(Task.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO make custom function in Task class (instead of __dict__)


# These top functions are what I had used.







    def add_response(self, address, time, value, task, worker):
        """
        write response of tested address to db
        """ # TODO update last time of task
        # TODO obsolete since worker sync
        result = Response(
            address=address,
            time=int(time),
            value=int(value),
            task=task,
            worker=worker
        )
        with self.sessions.begin() as session:
            session.add(result)

    def get_avrg_response_all(self, date_from=None, date_to=None):
        """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optional
        """ # TODO time selection
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.address).distinct():
                address = item[0]
                # TODO optimize query
                value = session.query(func.avg(Response.value)).filter(Response.address == address).one()[0]
                outcome.append({"address": address, "value": int(value)})
        return outcome

    def get_response_summary(self, worker=False, time_from=False, time_to=False):
        """
            get info is detailed list of addresses (generate: number of addr records,
            first time testing, last time testing and average responsing time)
            # TODO filter by worker and task
        """
        outcome = []
        with self.sessions.begin() as session:
            for item in session.query(Response.address).distinct():
                address = item[0]
                query = session.query(Response).filter(Response.address == address)
                if worker:
                    query = query.filter(Response.worker == worker)
                if time_from:
                    query = query.filter(Response.time > time_from)
                if time_to:
                    query = query.filter(Response.time < time_to)
                outcome.append({
                    "address": address,
                    "first_response": query.order_by(Response.time).first().time,
                    "last_response": query.order_by(Response.time.desc()).first().time,
                    "average": query.with_entities(func.avg(Response.value)).one()[0],
                    "count": query.count()
                })
        return {"status": "200", "data": outcome}

    def get_worker_tasks(self, worker):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task).filter(Task.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO make custom function in Task class (instead of __dict__)

    def sync_worker(self, data):
        """
        Sync worker - store responses and return tasks
        """
        print("syncWorker")
        with self.sessions.begin() as session:
            worker_id = session.query(Worker).filter(Worker.token == data["api"])
            for response in data["responses"]:
                result = Response(
                    address=response["address"],
                    time=response["time"],
                    value=response["value"],
                    task=response["task"],
                    worker=data["worker"]
                )
                session.add(result)
                # TODO alter task last update

            print(str(data))
            for hostStatus in data["hosts_availability"]:
                print(str(hostStatus))
                result = HostStatus(
                    worker_id = data["worker"]
                    address = data["address"]
                    time_from = data["time_from"]
                    time_to = data["time_to"]
                    available = data["available"]
                )
                session.add(result)

            tasks = session.query(Task).filter(Task.worker == data["worker"])
            return [item.__dict__ for item in tasks.all()] # TODO make custom function in Task class (instead of __dict__)

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()
            session.query(Address).delete()

    def get_responses(self, worker=False, task="ping"):
        """
        Return list of responses.
        """
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.task == task)
            if worker:
                query.filter(Response.worker == worker)
            return [item.__dict__ for item in query.all()] # TODO custom function

    def update_address(self, address_data):
        """
        Update address. If address does not exist, create it.
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address_data["address"]).first()
            if address is None:
                address = Address(
                    address=address_data["address"],
                )
                session.add(address)
                status = {"status": "Created"}
            else:
                status = {"status": "Updated"}
            data_keys = ["location", "latitude", "longitude", "note"]
            for key in data_keys:
                if key in address_data:
                    setattr(address, key, address_data[key])
            return status

    def delete_address(self, address_data):
        """
        Delete address if exists - according ip address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address_data["address"]).first()
            if address is None:
                return {"status": "500"}
            else:
                session.delete(address)
                return {"status": "200"}

    def get_address(self, address):
        """
        Get information about IP address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address).first()
            if address is None:
                return {"status": "500"}
            else:
                return {"status": "200", "data": address.values()}

    def get_address(self, address):
        """
        Get information about IP address
        """
        with self.sessions.begin() as session:
            address = session.query(Address).filter(Address.address == address).first()
            if address is None:
                return {"status": "545"}
            else:
                return {"status": "200", "data": address.values()}

    def get_all_addresses(self):
        """
        Return all addresses
        """
        with self.sessions.begin() as session:
            query = session.query(Address)
            return {"status": "200", "data": [item.values() for item in query.all()]}
