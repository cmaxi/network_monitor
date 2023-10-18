from sqlalchemy import Column, Integer, String, TIMESTAMP
from pydantic import BaseModel
from sqlalchemy.sql import func

class BaseItem():
    """
    Attributes common for Response and Task.
    """
    id = Column(Integer, primary_key=True)
    address = Column(String(100))
    createdAt = Column(TIMESTAMP, server_default=func.now())
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())


class BaseResponse(BaseItem):
    """
    Outcome of any task/test/measurement.
    """
    __tablename__ = 'responses'

    task = Column(String(100))
    time = Column(Integer)
    value = Column(Integer)

class BaseResponseSchema(BaseModel):
    task: str
    time: int
    value: int

class BaseTask():
    """
    Definition of task.
    """
    __tablename__ = 'tasks'
    id = Column(Integer, primary_key=True)
    task = Column(String(100))
    frequency = Column(String(5))
    last_run = Column(Integer, default=0)
    timeout = Column(Integer, default=1)
    retry = Column(Integer, default=0)
    retry_time = Column(Integer, default=1000)
    treshold = Column(Integer, default=50)
    retry_data = Column(String(300))

class BaseTaskWorker(BaseTask):
    address = Column(String(100))


class BaseTaskSchema(BaseModel):
    task: str
    frequency: str
    last_run: int
