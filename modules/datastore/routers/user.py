from fastapi import APIRouter, Depends, HTTPException,Security
from fastapi.security import SecurityScopes
from modules.datastore.OAuth2 import OAuth2, User, Token
from modules.datastore.sql_connector import SqlConnection, SqlUser


router = APIRouter(
    prefix="/user",
    tags=["user"],
    dependencies=[Depends(OAuth2)],
    responses={404: {"description": "Not found"}},
)

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlUser = SqlUser(session)

@router.get("/", status_code=200)
async def read_items():
    return 2

@router.get("/getHash", status_code=200)#get all responses for graph
async def get_user_hash(username):
    """
        generate JSON of all response times by time
    """
    return sqlUser.get_hash(username)

@router.get("/users/me/", response_model=User, status_code=200)
async def read_users_me(current_user: User = Depends(oauth2.get_current_active_user)):
    return current_user

@router.post("/create")
async def add_user(username: str, password: str, role: int,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"]), status_code=200):
    hashed_password = oauth2.get_password_hash(password)
    sqlUser.create(username=username, hashed_password=hashed_password, role=role)

@router.get("/items/") #testing purpose / oauth2
async def read_items(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    return [{"item_id": "Foo", "owner": current_user.username}]