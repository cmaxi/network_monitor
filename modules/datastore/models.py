"""
Models adjusted for datastore.

TODO: add Worker model - to store its GPS
"""
from __future__ import annotations
from typing import List
from sqlalchemy import ForeignKey, func
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, Integer, Boolean, TIMESTAMP
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from pydantic import BaseModel
from sqlalchemy.sql import func


from modules.models import BaseTask, BaseResponse, BaseItem, BaseTaskSchema, BaseResponseSchema

class Base(DeclarativeBase):
    createdAt = Column(TIMESTAMP, server_default=func.now())
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

class Base1(DeclarativeBase):
    createdAt = Column(TIMESTAMP, server_default=func.now())
    updatedAt = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())
    


class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    worker = Column(String(100))

    def values(self):
        """
        Return values for api client.
        """
        return {
            "address": self.address,
            "task": self.task,
            "time": self.time,
            "value": self.value,
            "worker": self.worker
        }

class ResponseSchema(BaseResponseSchema):
    address: str
    worker: str

"""
class Task(BaseTask, Base):
    #Definition of task.


    
    worker = Column(String(100))
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    color = Column(String(10))
    runing = Column(Boolean)
    hide = Column(Boolean)
"""

class HostStatus(Base):
    __tablename__ = 'host_status'
    id = Column(Integer, primary_key=True)
    worker_id = Column(Integer)
    address = Column(String(15))
    time_from = Column(Integer)
    time_to = Column(Integer)
    available = Column(Boolean)

class Address(Base1, BaseItem):
    """
    IP address meta data
    """
    __tablename__ = 'addresses'
    name = Column(String(100))
    location = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    note = Column(String(500))
    color = Column(String(10))
#    runing = Column(Boolean)    
    task = relationship("Task", back_populates="address")

    def values(self):
        """
        Return values for api client.
        """
        return {
            "address": self.address,
            "name": self.name,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "note": self.note,
            "color": self.color,
        }

class Users(Base):
    """
    
    """
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String(100), unique=True)
    hashed_password = Column(String(100))
    role = Column(Integer)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "username": self.username,
            "hashed_password": self.hashed_password,
            "role": self.role,
        }

worker_has_task = Table(
    "worker_has_task",
    Base1.metadata,
    Column("worker_id", ForeignKey("workers.id")),
    Column("task_id", ForeignKey("tasks.id")),
)

class Worker(Base1):
    """
    
    """
    __tablename__ = 'workers'
    id: Mapped[int] = mapped_column(primary_key=True)
    task = relationship("Task", secondary=worker_has_task)
    name = Column(String(100))
    token = Column(String(100))

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,

        }

class Task(Base1, BaseTask):
    """
    
    """
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    address_id = mapped_column(ForeignKey("addresses.id"))
    address = relationship("Address", back_populates="task")
 #   name = Column(String(100))
#    latitude = Column(Float)
#    longitude = Column(Float)
#    color = Column(String(10))
    running = Column(Boolean)
    hide = Column(Boolean)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,
            "running": self.running,
            "hide": self.hide,
            "address": self.address.address,
            "task": self.task,
            "frequency": self.frequency,
            "name": self.address.name,
            "location": self.address.location,
            "latitude": self.address.latitude,
            "longitude": self.address.longitude,
            "note": self.address.note,
            "color": self.address.color,
            "timeout": self.timeout,
            "retry": self.retry,
            "treshold": self.treshold,
            "retry_data": self.retry_data,
        }

class UserHasWorker(Base):
    """
    
    """
    __tablename__ = 'user_has_worker'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    worker_id = Column(Integer)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,

        }

def make_tables(engine):
    """
    Create tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
    Base1.metadata.create_all(engine, checkfirst=True)

def init_data(engine):
    """
    with engine.begin() as session:
        #usersCount = session.query(func.count(Users.id))
        #return usersCount

    with engine.begin() as session:
        engine.add(Users(username='admin', hashed_password='$2b$12$7Ss7bF7YgMdcLD0Ax2udbuCRUAKoQ8u.ebPUdpwHAWiWgrzLoUTgK', role='1'))

    result = Worker(
        name='initWorker',
        token='9d207bf0-10f5-4d8f-a479-22ff5aeff8d1'
    )

    with engine.begin() as session:
        engine.add(result)
    """
    return {"status": "200"}
