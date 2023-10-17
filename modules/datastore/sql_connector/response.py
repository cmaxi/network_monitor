from modules.sql_connector import CommonSqlConnector
from modules.datastore.models import Response, Task, Address, Users, Worker, worker_has_task
from modules.datastore.schema import ResponseGet, ResponseGetWorker, ResponseAdd
from modules.datastore.data_validation import DataValidation
from sqlalchemy.sql import func, exists

class SqlResponse(CommonSqlConnector):
    def __init__(self, db_connection):
        """
        Init the sql connector (connect, prepare tables).
        """
        self.sessions = db_connection

    def get_all(self, data: ResponseGet):
        """
        generate JSON of all responses
        """ # TODO time selection
        try:
            with self.sessions.begin() as session:
                if data.time_from!=None and data.time_to!=None:
                    query = session.query(Response).filter(Response.time >= data.time_from, Response.time <= data.time_to)
                elif data.time_from == None and data.time_to != None:
                    query = session.query(Response).filter(Response.time <= data.time_to)
                elif data.time_from != None and data.time_to == None:
                    query = session.query(Response).filter(Response.time >= data.time_from)
                else:
                    query = session.query(Response)
                
                if data.limit is not None:
                    query = query.limit(data.limit)

                return [item.values() for item in query.all()]
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )
    

    def delete_address(self, address):
        try:
            with self.sessions.begin() as session:
                addressResponses = session.query(Response).filter(Response.address == address).delete()
                return {"smazano zaznamu: ": addressResponses}
        except:
           raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            ) 

    def delete_all(self):
        """
        delete all responses
        """
        try:
            with self.sessions.begin() as session:
                count = session.query(Response).delete()
                return {"smazano zaznamu: ": count}
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )

    def add(self, data: ResponseAdd):
        """
        write response of tested address to db
        """ # TODO update last time of task
        # TODO obsolete since worker sync
        result = Response(
            address=data.address,
            time=data.time,
            value=data.value,
            task=data.task,
            worker=data.workerId
        )
        try:
            with self.sessions.begin() as session:
                session.add(result)
                session.flush()
                session.refresh(result)
                return result.values()
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )
    
    def get_avrg_all(self, data: ResponseGet):
        """
        generate JSON of average response time of each ip addresses, dateFrom and dateTo are optional
        """ # TODO time selection
        outcome = []
        try:
            with self.sessions.begin() as session:
                for item in session.query(Response.address).distinct():
                    address = item[0]
                    # TODO optimize query
                    value = session.query(func.avg(Response.value)).filter(Response.address == address).one()[0]
                    outcome.append({"address": address, "value": int(value)})
            return outcome
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )

    ## TODO: validate worker (if does not exist, than internal error)
    def get_summary(self, data: ResponseGetWorker):
        """
            get info is detailed list of addresses (generate: number of addr records,
            first time testing, last time testing and average responsing time)
            # TODO filter by worker and task
        """
        outcome = []
        try:
            with self.sessions.begin() as session:
                for item in session.query(Response.address).distinct():
                    address = item[0]
                    query = session.query(Response).filter(Response.address == address)
                    if data.workerId:
                        query = query.filter(Response.worker == data.workerId)
                    if data.time_from:
                        query = query.filter(Response.time > data.time_from)
                    if data.time_to:
                        query = query.filter(Response.time < data.time_to)
                    outcome.append({
                        "address": address,
                        "first_response": query.order_by(Response.time).first().time,
                        "last_response": query.order_by(Response.time.desc()).first().time,
                        "average": query.with_entities(func.avg(Response.value)).one()[0],
                        "count": query.count()
                    })
            return outcome
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )

    def get(self, worker=False, task="ping"):
        """
        Return list of responses.
        """
        try:
            with self.sessions.begin() as session:
                query = session.query(Response).filter(Response.task == task)
                if worker:
                    query.filter(Response.worker == worker)
                return [item.__dict__ for item in query.all()] # TODO custom function
        except:
            raise HTTPException(
                status_code=500,
                detail="Unknown database error"
            )

    
    
