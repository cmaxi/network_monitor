from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, ValidationError
from typing import List, Union
from fastapi import Depends,Security


from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,SecurityScopes, APIKeyHeader, APIKeyQuery
from modules.datastore.sql_connector import SqlConnection, SqlAddress, SqlOther, SqlResponse, SqlTask, SqlUser


from passlib.context import CryptContext
from datetime import datetime, timedelta


class User(BaseModel):
    username: str
    email: Union[str, None] = None
    full_name: Union[str, None] = None
    disabled: Union[bool, None] = None
    role: Union[int, None] = None

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):

    username: Union[str, None] = None
    scopes: List[int] = []

class UserInDB(User):
    hashed_password: str



class OAuth2:
    SECRET_KEY = "885da96a8e6ff8ddfeb25f6196a93cd8f677c46097cc60df2c5812021281da49"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30


    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


    oauth2_scheme = OAuth2PasswordBearer(
        tokenUrl="token",
        scopes={"1": "administrator", "2": "viewer"},
    )
    sql_connection = SqlConnection()
    session = sql_connection.getSession()
    sqlUser = SqlUser(session)


    def get_access_token_expires(self):
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        return self.pwd_context.hash(password)
 

    def get_user(self, username: str):
        user = {'username': username, 'hashed_password': OAuth2.sqlUser.get_hash(username), 'role': OAuth2.sqlUser.get(username)}
        return UserInDB(**user)

    def authenticate_user(self, username: str, password: str):
        user = self.get_user(username)
        if not self.verify_password(password, self.sqlUser.get_hash(username)):
            return False
        return user

    def create_access_token(self, data: dict, expires_delta: Union[timedelta, None] = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    async def get_current_user(security_scopes: SecurityScopes, token: str = Depends(oauth2_scheme)):
        oauthClass = OAuth2()
        if security_scopes.scopes:
            authenticate_value = f'Bearer scope="{security_scopes}"'
        else:
            authenticate_value = "Bearer"
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentialss",
            headers={"WWW-Authenticate": authenticate_value},
        )
        try:
            #SECRET_KEY = "885da96a8e6ff8ddfeb25f6196a93cd8f677c46097cc60df2c5812021281da49"
            #ALGORITHM = "HS256"
            payload = jwt.decode(token, oauthClass.SECRET_KEY, algorithms=[oauthClass.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception
            token_scopes = payload.get("scopes", [])
            token_data = TokenData(scopes=token_scopes, username=username)
        except (JWTError, ValidationError):
            raise credentials_exception
        except JWTError:
            raise credentials_exception
        
        user = oauthClass.get_user(username=token_data.username)
        if user is None:
            raise credentials_exception

        if any(scope in security_scopes.scopes for scope in str(token_data.scopes)):
            return user
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
        """       
        for scope in security_scopes.scopes:
            print("scope: " + scope)
            if scope not in str(token_data.scopes):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not enough permissions",
                    headers={"WWW-Authenticate": authenticate_value},
                )
        """
        return user


    async def get_current_active_user(self, current_user: User = Security(get_current_user, scopes=["1"])):
        if current_user.disabled:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user


