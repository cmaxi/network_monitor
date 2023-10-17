from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, Boolean, String

from modules.models import BaseTaskWorker, BaseResponse

Base = declarative_base()

class Response(BaseResponse, Base):
    """
    Outcome of any task/test/measurement.
    """
    synced = Column(Boolean)

    def sync_values(self):
        return {
            "id": self.id,
            "address": self.address,
            "task": self.task,
            "time": self.time,
            "value": self.value
        }


class Task(BaseTaskWorker, Base):
    """
    Definition of task.
    """
    active = Column(Integer)
    next_run = Column(Integer, default=0)
    available = Column(Boolean, default=0)
    available_from = Column(Integer)
    retry_count = Column(Integer, default=0)

    def values(self):
        return {
            "address": self.address,
            "active": self.active,
            "frequency": self.frequency,
            "task": self.task,
            "next_run": self.next_run,
            "last_run": self.last_run,
            "available": self.available,
            "available_from": self.available_from,
            "treshold": self.treshold,
            "timeout": self.timeout,
            "retry": self.retry,
            "retry_count": self.retry_count,
            "retry_time": self.retry_time,
            "retry_data": self.retry_data
        }


class HostStatus(Base):
    __tablename__ = 'host_status'
    id = Column(Integer, primary_key=True)
    address = Column(String(15))
    time_from = Column(Integer)
    time_to = Column(Integer)
    available = Column(Boolean)
    synced = Column(Boolean, default=False)

    def sync_values(self):
        return {
            "id": self.id,
            "address": self.address,
            "time_from": self.time_from,
            "time_to": self.time_to,
            "available": self.available,
        }

def make_tables(engine):
    """
    Crate tables if they do not exist.
    """
    Base.metadata.create_all(engine, checkfirst=True)
