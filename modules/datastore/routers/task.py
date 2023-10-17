from fastapi import APIRouter, Depends, HTTPException,Security, Response
from modules.datastore.sql_connector import SqlConnection, SqlTask
from modules.datastore.OAuth2 import OAuth2, User, Token
from modules.datastore.models import Task
from modules.datastore.schema import TaskIn, TaskOut, TaskAssociate
from typing import Any



router = APIRouter(
    prefix="/task",
    tags=["task"],
    responses={404: {"description": "Not found"}},
)

oauth2 = OAuth2()
sql_connection = SqlConnection()
session = sql_connection.getSession()
sqlTask = SqlTask(session)


@router.post("/", status_code=200)#insert address
async def create_new(task: TaskIn, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        create new TASK
    """
#    data = [address, task, time, worker, latitude, longitude, color, name, runing, hide]
#    print("přidá: ", data)
    return sqlTask.create(task)


@router.post("/associate", status_code=200) #associtate task to worker
async def associate(data: TaskAssociate, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        create association between worker and task
    """
    return sqlTask.associate(data)


@router.delete("/{task_id}", status_code=200) #delete address from task table and responses of address
async def delete(task_id: int,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        delete task by id
    """
    return sqlTask.delete(task_id)

@router.delete("/associate-delete", status_code=200) #delete address from task table and responses of address
async def delete_association(data:TaskAssociate,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        delete association between worker and task
    """
    return sqlTask.associate_delete(data)

@router.put("/", status_code=200)#update tasks dont remove data
async def update_task(data: TaskOut, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        update task
    """
    return sqlTask.update(data)

@router.get("/pause/{task_id}", status_code=200) #Pause task
async def pause(task_id:int, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        pause task
    """
    return sqlTask.pause(task_id)

@router.get("/active/{task_id}", status_code=200) #Activate task
async def active(task_id:int, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        activate task
    """
    return sqlTask.active(task_id)


@router.get("/hide{task_id}", status_code=200) #Hide task
async def hide(task_id:int, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        hide task
    """
    return sqlTask.hide(task_id)

@router.get("/unhide{task_id}", status_code=200) #unhide task
async def unhide(task_id:int, current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
        unhide task
    """
    return sqlTask.unhide(task_id)

@router.get("/workers-task/{worker_id}", status_code=200)
def get_worker_tasks(worker_id:int,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return all tasks for given worker
    """
    return sqlTask.WorkersTask(worker_id)

@router.get("/active-tasks/{worker_id}", status_code=200)
def get_active_task(worker_id:int,current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return active tasks for given worker
    """
    return sqlTask.getActiveTasks(worker_id)

@router.get("/", status_code=200)
def get_all_tasks(current_user: User = Security(oauth2.get_current_active_user, scopes=["1"])):
    """
    Return all tasks
    """
    return sqlTask.getTasks()
