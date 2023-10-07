"""
Fast api setup and routes for datastore.
"""
from fastapi import Request, FastAPI, HTTPException, status, Security
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm,SecurityScopes, APIKeyHeader, APIKeyQuery

from settings import TESTING
from modules.datastore.OAuth2 import OAuth2, User, Token

from modules.datastore.sql_connector import SqlConnection, SqlAddress, SqlOther, SqlResponse
from modules.datastore.routers import user, task, response, address
from modules.datastore.schema import syncWorker


oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlAddress = SqlAddress(session)
sqlResponse = SqlResponse(session)
sqlOther = SqlOther(session)


if TESTING:
    sqlOther.clear_all_tables()

app = FastAPI()
app.include_router(user.router)
app.include_router(task.router)
app.include_router(response.router)
app.include_router(address.router)
print("https://127.0.0.1:8000/docs")  # link to default FastAPI browser

@app.get("/")
def read_root():
    """ access via FastApi, root directory return true value """
    return {"status": True}
    
#API KEY authentization for workers, they can authorize via query or header
api_key_query = APIKeyQuery(name="api-key", auto_error=False)
api_key_header = APIKeyHeader(name="x-api-key", auto_error=False)
def get_api_key(api_key_query: str = Security(api_key_query), api_key_header: str = Security(api_key_header)):
    """
    find worker_id by api_key
    """
    worker_id = sqlOther.get_worker(api_key_query)

    # 
    if api_key_query is not None:
        worker_id = sqlOther.get_worker(api_key_query)
        if worker_id is not None:
            return api_key_query

    if api_key_header is not None:
        worker_id = sqlOther.get_worker(api_key_header)
        if worker_id is not None:
            return api_key_header

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing API Key",)


"""
Login user, if 
"""
@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # find user by username and password
    user = oauth2.authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    # set expires, create oauth2 token
    access_token_expires = oauth2.get_access_token_expires()
    access_token = oauth2.create_access_token(
        data={"sub": user.username, "scopes": [user.role]},
        expires_delta=access_token_expires,
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/get-all-responses-from")#get all responses for graph
def get_responses_from(timeFrom):
    """
        generate JSON of all response times by time from time
    """
    return sql_conn.get_all_responses_from(timeFrom)


#create task
@app.post("/create-task")
async def put_new(address, task, time, worker):
    """
        generate JSON of all response times by time
    """
    data = [address,task,time,worker]
    print("add task: ", data)
    return sql_conn.create_task(data)


#testing endpoint for apiKey authentization
@app.get("/private")
def private(api_key: str = Security(get_api_key)):
    """A Private endpoint that requires a valid API key be provided"""
    return f"Private Endpoint. API Key is: {api_key}"

#get all workers
@app.get("/workers")
def workers(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    return sqlOther.get_workers()

#create new worker
@app.get("/create-worker")
def createWorker(worker_name, api_key, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    return sqlOther.create_worker(worker_name, api_key)

#sync worker to datastore
# TODO authorization
@app.post("/sync-worker")
async def sync_worker(request: syncWorker):
    """
    Worker synchronization:
    accept responses for storage
    return list of tasks for given worker
    """
    return sqlOther.sync_worker(request)

# ?
@app.get("/report", response_class=HTMLResponse)
async def make_report():
    """
    Create and return html report.
    """
    worker = "default"
    responses = sqlResponse.get_responses(worker=worker)

    df = old_report.responses2df(responses)

    html_content = []
    html_content += old_report.get_histogram(df)
    html_content += old_report.get_linear(df)
    html_content += old_report.get_bar(df)

    html_str = "\n".join(html_content)

    return HTMLResponse(content=html_str, status_code=200)


@app.get("/map", response_class=HTMLResponse)
async def make_map(latitude=50.0755, longitude=14.4378):
    """
    Create a folium map.
    use as: http://127.0.0.1:8000/map?longitude=200&latitude=10

    TODO: it should be worker latitude and longitude
    TODO: maybe join sql request instead of manual joining
    """
    worker = "default"
    annotated_addresses = sqlAddress.get_all_addresses()
    address_summaries = sqlResponse.get_response_summary(worker=worker)

    addresses = []
    for address in annotated_addresses["data"]:
        for summary in address_summaries["data"]:
            if address["address"] == summary["address"]:
                address.update(summary)
                addresses.append(address)

    html_str = old_report.get_map(addresses, latitude, longitude)

    return HTMLResponse(content=html_str, status_code=200)



#app.mount("/media", StaticFiles(directory="media"), name="media")
