from fastapi import APIRouter, Depends, HTTPException,Security,Request
from modules.datastore.sql_connector import SqlConnection, SqlAddress
from typing import Optional
from modules.datastore.models import Response, Task, Address
from typing import Any
from modules.datastore.schema import AddressIn, AddressOut, AddressDelete


router = APIRouter(
    prefix="/address",
    tags=["address"],
    responses={404: {"description": "Not found"}},
)

from modules.datastore.OAuth2 import OAuth2, User, Token

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlAddress = SqlAddress(session)

@router.get("/", status_code=200)
def get_all():
    """
    Get all addresses
    """
    return sqlAddress.get_all()

@router.get("/{address}", response_model=AddressOut, status_code=200)
def get(address):
    """
    Get address specified in request provided data
    """
    return sqlAddress.get(address)

@router.put("/", response_model=AddressOut, status_code=200)
async def update(data: AddressIn)->Any:
    """
    Update address from provided data
    """
    return sqlAddress.update(data)

@router.post("/", response_model=AddressOut, status_code=200)
async def create_Address(request: AddressIn)->Any:
    """
    Create address from provided data
    """
    data = sqlAddress.create(request)
    return data

@router.delete("/", status_code=200)
async def delete(request: AddressDelete):
    """
    Delete address specified in request provided data
    """
    return sqlAddress.delete(request)