import uuid

from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import List, Optional, Union
from datetime import datetime

app = FastAPI()


# main model
class Task(BaseModel):
    id: Optional[str] = uuid.uuid4().hex
    title: str
    description: str
    creation_date: Optional[datetime] = datetime.now()


# update model
class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None


# filter model
class TaskFilter(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    min_creation_date: Optional[datetime] = None
    max_creation_date: Optional[datetime] = None


# task with file model
class TaskWithFile(Task):
    file_url: Optional[str] = None


# category model
class TaskCategory(BaseModel):
    category: Optional[str] = None


# storage
tasks = {}
tasks_with_files_and_categories = {}


# API without files
@app.post("/tasks/", response_model=Task)
def create_task(task: Task):
    tasks[task.id] = task
    return task


@app.get("/tasks/", response_model=List[Task])
def list_tasks():
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")
    return tasks[task_id]


@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: str, task_update: TaskUpdate):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]
    if task_update.title is not None:
        task.title = task_update.title
    if task_update.description is not None:
        task.description = task_update.description

    tasks[task_id] = task
    return task


@app.delete("/tasks/{task_id}", response_model=Task)
def delete_task(task_id: str):
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks.pop(task_id)
    return task


# API with files
@app.post("/tasks_with_file/", response_model=TaskWithFile)
def create_task_with_file(task: Task, file: UploadFile = File(None)):
    task_id = task.id
    if file:
        file_url = f"/files/{task_id}/{file.filename}"
    else:
        file_url = None

    task_with_file = TaskWithFile(**task.dict(), file_url=file_url)
    tasks_with_files_and_categories[task_id] = task_with_file
    return task_with_file


@app.get("/tasks_with_file/", response_model=List[TaskWithFile])
def list_tasks_with_file(filter: TaskFilter = None):
    filtered_tasks = tasks_with_files_and_categories.values()

    if filter:
        if filter.title:
            filtered_tasks = [
                task for task in filtered_tasks if filter.title in task.title
            ]
        if filter.description:
            filtered_tasks = [
                task
                for task in filtered_tasks
                if filter.description in task.description
            ]
        if filter.min_creation_date:
            filtered_tasks = [
                task
                for task in filtered_tasks
                if task.creation_date >= filter.min_creation_date
            ]
        if filter.max_creation_date:
            filtered_tasks = [
                task
                for task in filtered_tasks
                if task.creation_date <= filter.max_creation_date
            ]

    return list(filtered_tasks)


@app.put("/tasks_with_file/{task_id}", response_model=TaskWithFile)
def update_task_with_file(
    task_id: str,
    task_update: Union[TaskUpdate, TaskCategory],
    file: UploadFile = File(None),
):
    if task_id not in tasks_with_files_and_categories:
        raise HTTPException(status_code=404, detail="Task not found")

    task_with_file = tasks_with_files_and_categories[task_id]

    if isinstance(task_update, TaskUpdate):
        if task_update.title:
            task_with_file.title = task_update.title
        if task_update.description:
            task_with_file.description = task_update.description
    elif isinstance(task_update, TaskCategory):
        task_with_file.category = task_update.category

    if file:
        file_url = f"/files/{task_id}/{file.filename}"

        task_with_file.file_url = file_url

    tasks_with_files_and_categories[task_id] = task_with_file
    return task_with_file


@app.delete("/tasks_with_file/{task_id}", response_model=TaskWithFile)
def delete_task_with_file(task_id: str):
    if task_id not in tasks_with_files_and_categories:
        raise HTTPException(status_code=404, detail="Task not found")

    task_with_file = tasks_with_files_and_categories.pop(task_id)
    return task_with_file
