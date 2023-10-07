from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from sqlalchemy.sql import func, exists

class SqlUser(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def get(self, username):
        with self.sessions.begin() as session:
            result = session.query(Users).filter(Users.username == username).one()
            return result.role

    def create(self, username, hashed_password, role):
            print(username, hashed_password, role)
            with self.sessions.begin() as session:
                    session.add(Users(username=username, hashed_password=hashed_password, role=role))
            return {"status": "200"}

    def get_hash(self, username):
        with self.sessions.begin() as session:
            result = session.query(Users).filter(Users.username == username).one()
            return result.hashed_password
            
    