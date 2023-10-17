from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from sqlalchemy.sql import func, exists
from fastapi import HTTPException


class SqlUser(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection
        self.check_and_insert_default_data()

    def get(self, username):
        with self.sessions.begin() as session:
            result = session.query(Users).filter(Users.username == username).first()
            if result:
                return result.role
            else:
             raise HTTPException(
                status_code=400,
                detail="Username not found or bad password"
             )

    def create(self, username, hashed_password, role):
            print(username, hashed_password, role)
            with self.sessions.begin() as session:
                    session.add(Users(username=username, hashed_password=hashed_password, role=role))
            return {"status": "200"}

    def get_hash(self, username):
        with self.sessions.begin() as session:
            result = session.query(Users).filter(Users.username == username).first()
            if result:
                return result.hashed_password
            else:
             raise HTTPException(
                status_code=400,
                detail="Username not found or bad password"
             )
            
    def check_and_insert_default_data(self):
        with self.sessions.begin() as session:
            if not session.query(Users).first():
                # Vytvořte instance ORM modelů a nastavte jim výchozí data
                user = Users(
                    username = "admin",
                    hashed_password = "$2b$12$Pjgg3tarr556qmdX04081.v8SwVMTF0VLlrk/C6IhWiW9peGonzqy",
                    role = "1"
                )

                # Přidejte instance do databáze
                session.add(user)

                # Uložte změny do databáze
                session.commit()
    