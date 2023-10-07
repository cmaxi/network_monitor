from pydantic import BaseModel, Field
from typing import Optional, List

class AddressIn(BaseModel):
    address: str
    name: str
    location: str
    latitude: float
    longitude: float
    note: Optional[str]
    color: str

class AddressOut(AddressIn):
    id: int

class AddressDelete(BaseModel):
    address:str

class TaskIn(BaseModel):
#    worker: int
#    address: str
#    name: str
#    latitude: float
#    longitude: float
#    color: str
    address_id: int
    running: bool = Field(default=True)
    hide: bool = Field(default=False)
    task: str
    frequency: str

class TaskOut(TaskIn):
    id: int

class TaskAssociate(BaseModel):
    taskId: int
    workerId: int

class TaskId(BaseModel):
    id: int

class Response(BaseModel):
    address: str
    time: int
    value: int
    task: str

class HostStatus(BaseModel):
    address: str
    time_from: int
    time_to: int
    available: bool

class syncWorker(BaseModel):
    responses: Optional[List[Response]]
    hosts_availability: Optional[List[HostStatus]] 
    api: str