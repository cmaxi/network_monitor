from sqlalchemy.sql import func, exists
import sqlalchemy as db
from sqlalchemy import event
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine import Engine
import sqlite3 #  i have added this if you find better way to handle databases, you can remove it

from settings import DATASTORE_DATABASE
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.models import make_tables, init_data
from modules.sql_connector import CommonSqlConnector
from modules.datastore.data_validation import DataValidation

class SqlConnection(CommonSqlConnector):
    def __init__(self):
            """
            Init the sql connector (connect, prepare tables).
            """
            try:
                engine = db.create_engine('sqlite:///{}'.format(DATASTORE_DATABASE), echo=False)
                make_tables(engine)
                init_data(engine)            
            except:
                raise SystemExit('Sqlite is not available')
            self.sessions = sessionmaker(engine)
            

    def getSession(self):
        return self.sessions

    #Kvuli kontrole foreign key: https://docs.sqlalchemy.org/en/20/dialects/sqlite.html#foreign-key-support
    @event.listens_for(Engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()