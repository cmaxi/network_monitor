from enum import Enum
from pydantic import BaseModel, Field,Json, validator
from typing import Optional, List
from modules.datastore.data_validation import DataValidation

class TaskEnum(str, Enum):
    ping = "ping"

class AddressIn(BaseModel):
    address: str
    name: str
    location: str
    latitude: float
    longitude: float
    note: Optional[str]
    color: str

    @validator('address')
    def validateAddress(cls, value):
        validation = DataValidation()
        return validation.validate_ip_address(value)

class AddressOut(AddressIn):
    id: int

class AddressDelete(BaseModel):
    address:str

    @validator('address')
    def validateAddress(cls, value):
        validation = DataValidation()
        return validation.validate_ip_address(value)

class TaskIn(BaseModel):
    address_id: int
    running: bool = Field(default=True)
    hide: bool = Field(default=False)
    task: TaskEnum
    frequency: str
    retry: Optional[int] = Field(default=0)
    timeout: Optional[int] = Field(default=1)
    treshold: Optional[int] = Field(defalut=50)
    retry_data: Optional[dict]

    @validator('frequency')
    def validateAddress(cls, value):
        validation = DataValidation()
        return validation.validate_frequency_format(value)
        
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
    task: TaskEnum

    @validator('address')
    def validateAddress(cls, value):
        validation = DataValidation()
        return validation.validate_ip_address(value)

class ResponseAdd(Response):
    workerId: int

class ResponseGet(BaseModel):
    time_from: Optional[int]
    time_to: Optional[int]
    limit: Optional[int]

class ResponseGetWorker(BaseModel):
    time_from: Optional[int]
    time_to: Optional[int]
    workerId: Optional[int]

class HostStatus(BaseModel):
    address: str
    time_from: int
    time_to: int
    available: bool

    @validator('address')
    def validateAddress(cls, value):
        validation = DataValidation()
        return validation.validate_ip_address(value)

class syncWorker(BaseModel):
    responses: Optional[List[Response]]
    hosts_availability: Optional[List[HostStatus]] 
    api: str