from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.data_validation import DataValidation
from modules.datastore.schema import TaskIn, TaskOut, TaskAssociate
from sqlalchemy.sql import func, exists
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError


class SqlTask(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def create(self, data: TaskIn):
        """
        add new task
        """ # TODO add colors and name to database
        test = DataValidation()
        result = Task(
            address_id=data.address_id,
            frequency=data.frequency,
            task=data.task,
            running=data.running,
            hide=data.hide
        )

        with self.sessions.begin() as session:
            existAddress = session.query(exists().where(Address.id == data.address_id)).scalar()
            if existAddress:
                session.add(result)
                session.flush()
                session.refresh(result)
                result = TaskOut(
                    id = result.id,
                    **data.dict()
                )
                return result
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Address not exists"
                )

 #       return {"status": DataValidation().IP()}


    def associate(self, data):
        try:
            with self.sessions.begin() as session:
                statement = worker_has_task.insert().values(task_id=data.taskId, worker_id=data.workerId)
                session.execute(statement)
                session.commit()
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="FOREIGN KEY ERROR"
            )

    def delete(self, task_id):
        """
        delete address from tasks
        """
        try:
            with self.sessions.begin() as session:
                addressTask = session.query(Task).filter(Task.id == task_id).delete()
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="Associate created"
            )

    def associate_delete(self, data: TaskAssociate):
        """
        delete address from tasks and responses of address
        """
        with self.sessions.begin() as session:
            statement = worker_has_task.delete().where(worker_has_task.c.id==data.taskId, worker_has_task.c.worker_id==data.workerId)
            session.execute(statement)
            session.commit()

    def update(self, data):
        """
        update task
        """
        result = {
            "id":data.id,
            "address_id":data.address_id,
            "frequency":data.frequency,
            "task":data.task,
            "running":data.running,
            "hide":data.hide,
        }

        try:
            with self.sessions.begin() as session:
                existAddress = session.query(Task).filter(Task.id == data.id).update(result)
                if not existAddress:
                    raise HTTPException(
                        status_code=400,
                        detail="Address not exists"
                )
                updated_task = session.query(Task).filter(Task.id == data.id).first()
                return updated_task.values()
        except IntegrityError as e:
            raise HTTPException(
                status_code=400,
                detail="FOREIGN KEY ERROR"
            )

    def pause(self, task_id):
        """
        pause task just remove task from list
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Task.id == task_id)).scalar()
            if record_exists:
                session.query(Task).filter(Task.id == task_id).update({"running":False})
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task does not exist"
                )

    
    def active(self, task_id):
        """
        activate task
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Task.id == task_id)).scalar()
            if record_exists:
                session.query(Task).filter(Task.id == task_id).update({"running":True})
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task does not exist"
                )

    def hide(self, task_id):
        """
        hide task
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Task.id == task_id)).scalar()
            if record_exists:
                session.query(Task).filter(Task.id == task_id).update({"hide":True})
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task does not exist"
                )

    def unhide(self, task_id):
        """
        unhide task
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Task.id == task_id)).scalar()
            if(record_exists):
                session.query(Task).filter(Task.id == task_id).update({"hide":False})
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task does not exist"
                )

    def WorkersTask(self, worker_id):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Worker.id == worker_id)).scalar()
            if record_exists:
                query = session.query(Task).join(Task, Worker.task).filter(Worker.id == worker_id)
                #query = session.query(Task).filter(Task.worker == worker)
                return [item.values() for item in query.all()] # TODO make custom function in Task class (instead of __dict__)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Worker does not exist"
                )


    def getTasks(self):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            query = session.query(Task)
            #query = session.query(Task).filter(Task.worker == worker)
            return [item.values() for item in query.all()] # TODO make custom function in Task class (instead of __dict__)

    def getActiveTasks(self, worker_id):
        """
        Returns list of tasks for requested worker.
        """
        with self.sessions.begin() as session:
            record_exists = session.query(exists().where(Worker.id == worker_id)).scalar()
            if record_exists:
                query = session.query(Task).join(Task, Worker.task).filter(Worker.id == worker_id).filter(Task.running == True)
                #query = session.query(Task).filter(Task.worker == worker)
                return [item.values() for item in query.all()] # TODO make custom function in Task class (instead of __dict__)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Worker does not exist"
                )

    

       