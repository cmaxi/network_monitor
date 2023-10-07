from sqlalchemy import Column, Integer, String
from pydantic import BaseModel

class BaseItem():
    """
    Attributes common for Response and Task.
    """
    id = Column(Integer, primary_key=True)
    address = Column(String(100))


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

class BaseTaskWorker(BaseTask):
    address = Column(String(100))


class BaseTaskSchema(BaseModel):
    task: str
    frequency: str
    last_run: int
