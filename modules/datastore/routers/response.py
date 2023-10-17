from fastapi import APIRouter, Depends, HTTPException,Security
from modules.datastore.sql_connector import SqlConnection, SqlResponse
from typing import Optional
from modules.datastore.schema import ResponseGet, ResponseGetWorker, ResponseAdd


router = APIRouter(
    prefix="/response",
    tags=["response"],
    responses={404: {"description": "Not found"}},
)

from modules.datastore.OAuth2 import OAuth2, User, Token

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlResponse = SqlResponse(session)

@router.post("/", status_code=200)
def add_response(data: ResponseAdd, current_user: User = Security(oauth2.get_current_active_user, scopes=["1","2"])):
    """
    create new row (response) into db
    """
    return sqlResponse.add(data)

@router.post("/get-all", status_code=200)#get all responses for graph
def get_all_responses(data: ResponseGet, current_user: User = Security(oauth2.get_current_active_user, scopes=["1","2"])):
    """
        generate JSON of all response times by time
    """
    return sqlResponse.get_all(data)

@router.delete("/delete-all", status_code=200)#delete all responses
async def delete_responses(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlResponse.delete_all()

@router.delete("/{address}", status_code=200)#delete all responses
async def delete_responses(address: str, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        generate JSON of all response times by time
    """
    return sqlResponse.delete_address(address)


@router.post("/get-average", status_code=200)
def get_avrg_response(data: ResponseGet, current_user: User = Security(oauth2.get_current_active_user, scopes=["1", "2"])):
    """
        generate JSON of average response time of each ip addresses,
        dateFrom and dateTo are optional
    """
    return sqlResponse.get_avrg_all(data)

@router.post("/get-summary", status_code=200)
def get_response_summary(data: ResponseGetWorker, current_user: User = Security(oauth2.get_current_active_user, scopes=["1","2"])):
    """
    get info is detailed list of addresses (generate: number of addr records,
    first time testing, last time testing and average responsing time)
    """
    return sqlResponse.get_summary(data)



