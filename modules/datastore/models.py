"""
Models adjusted for datastore.

TODO: add Worker model - to store its GPS
"""
from __future__ import annotations
from typing import List
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, String, Float, Integer, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship
from sqlalchemy import Table
from pydantic import BaseModel


from modules.models import BaseTask, BaseResponse, BaseItem, BaseTaskSchema, BaseResponseSchema

Base = declarative_base()

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


class Address(BaseItem, Base):
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
    runing = Column(Boolean)

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
    username = Column(String(100))
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

class Base1(DeclarativeBase):
    pass

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

class TaskPydantic(BaseModel):
    id: int
    address: str
    name: str
    latitude: int


class Task(Base1,BaseTask):
    """
    
    """
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(primary_key=True)
    address = Column(String(100))
    name = Column(String(100))
    latitude = Column(Float)
    longitude = Column(Float)
    color = Column(String(10))
    runing = Column(Boolean)
    hide = Column(Boolean)

    def values(self):
        """
        Return values for api client.
        """
        return {
            "id": self.id,
            "address": self.address,
            "name": self.name,
            "location": self.location,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "note": self.note,
            "color": self.color,
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
