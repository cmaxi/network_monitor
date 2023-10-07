"""
takes care of the connection to the database
"""
import sqlalchemy as db
from sqlalchemy.orm import sessionmaker

from settings import WORKER_DATABASE
from modules.worker.models import Response, Task, HostStatus
from modules.worker.models import make_tables
from modules.sql_connector import CommonSqlConnector
from modules.common import ms_time

class WorkerSqlConnector(CommonSqlConnector):
    """
    Extra sql operations required for Worker.
    """

    def __init__(self, worker):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.worker = worker
        try:
            engine = db.create_engine(f'sqlite:///{WORKER_DATABASE}', echo=False)
            make_tables(engine)
            self.sessions = sessionmaker(engine)
        except:
            raise SystemExit('Sqlite is not available, shutting down worker')

    def clear_all_tables(self):
        """
        Clear content from tables (for testing purposes mainly).
        """
        with self.sessions.begin() as session:
            session.query(Task).delete()
            session.query(Response).delete()

    def update_task(self, task_data):
        """Update information about execution of the given task.
        """
        with self.sessions.begin() as session:
            task = session.query(Task).filter(
                Task.address == task_data["address"],
                Task.task == task_data["task"],
            ).first()
            task.next_run = task_data["next_run"]
            task.last_run = task_data["last_run"]
            task.available = task_data["available"]
            if not task.available_from:
                task.available_from = task_data["last_run"]

    def get_tasks(self):
        """
        Get all tasks.
        """
        with self.sessions.begin() as session:
            query = session.query(Task)
            return [item.values() for item in query.all()]

    def add_response(self, response):
        """
        write response of tested address to database
        """
        result = Response(
            address=response["address"],
            time=response["time"],
            value=response["value"],
            task=response["task"],
            synced=False,
        )

        with self.sessions.begin() as session:
            query = session.query(Task).filter(Task.address == response["address"]).first()
            print("availability: " + str(query.available))
            query2 = session.query(Response).filter(Response.address == response["address"]).order_by(Response.id.desc()).first()
            if query2:
                lastValue =  query2.sync_values()["value"]
                newValue = response["value"]

                # Pokud se od posledniho pingu zmenila odezva, pak zapisu do DB
                if (lastValue == -1 and newValue != -1) or (lastValue != -1 and newValue == -1):
                    print("availability podminka: " + str(query.available))
                    print("lastValue: " + str(lastValue) + " new value: " + str(newValue))
                    result_host = HostStatus(
                        address=response["address"],
                        time_from=query.available_from,
                        time_to=response["time"],
                        available=query.available,
                    )
                    query.available_from = response["time"]
                    session.add(result_host)  
            session.add(result)

    def reset_tasks(self):
        """
        Reset tasks times on startup of application.
        """
        with self.sessions.begin() as session:
            session.query(Task).update({Task.last_run: 0, Task.next_run: 0})
    
    def createAvailable(self, task, response):
        """
        Available row not exist, than create
        usually when it receives a new task, or at startup
        """
        available = False
        if response != -1:
            available = True

        result = HostStatus(
            address=task["address"],
            time_from=task["last_run"],
            available=available,
        )
        with self.sessions.begin() as session:
            session.add(result)
        
        # Pokud neexistuje available, vytvorim novy zaznam v tabulce HostStatus
        # TODO: musim zkontrolovat, jestli neexistuje uz nejaky zaznam s neuzavrenym okenkem
        """
        if task["available"] == None:
            with self.sessions.begin() as session:
                session.add(result)
        else:
            with self.sessions.begin() as session:
                query = session.query(HostStatus).filter(HostStatus.address == task["address"], HostStatus.time_to == "").first()
                if query:
                    if available != query["available"]:
                        query.time_to = task["last_run"]  
                        session.add(result)                  
        """    

    def presync(self):
        """Function called before synchronization with datastore

        Should select responses that should be sent to datastore.
        """
        with self.sessions.begin() as session:
            query = session.query(Response).filter(Response.synced == False)
            return [item.sync_values() for item in query.all()]
    
    def presyncHosts(self):
        with self.sessions.begin() as session:
            query = session.query(HostStatus).filter(HostStatus.synced == False)
            return [item.sync_values() for item in query.all()]

    def postsync(self, tasks, responses, host_availability):
        """Fu r synchronization with datastore

        Tasks:
        - New tasks are created.
        - Already existing tasks are annotated with current timestamp and updated.
        - Stored tasks without current timestamp are deleted.

        Responses are marked as synced.
        """
        active_stamp = ms_time()
        with self.sessions.begin() as session:
            if responses:
                id_list = [item["id"] for item in responses]
                session.query(Response).filter(
                    Response.id.in_(id_list)).update({Response.synced: True})

            if host_availability:
                id_list = [item["id"] for item in host_availability]
                session.query(HostStatus).filter(
                    Response.id.in_(id_list)).update({HostStatus.synced: True})

            for incoming_task in tasks:
                existing_task = session.query(Task).filter(
                    Task.address == incoming_task["address"],
                    Task.task == incoming_task["task"]
                ).first()
                if existing_task is not None:
                    existing_task.frequency = incoming_task["frequency"]
                    existing_task.active = active_stamp
                else:
                    new_task = Task(
                        address=incoming_task["address"],
                        task=incoming_task["task"],
                        frequency=incoming_task["frequency"],
                        active=active_stamp,
                    )
                    session.add(new_task)
            session.query(Task).filter(Task.active < active_stamp).delete()
