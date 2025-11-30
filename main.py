from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import TaskModel

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize the FastAPI app
app = FastAPI(title="Task Manager", description="Task management API")

# Pydantic model for Task
class Task(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True

class TaskCreate(BaseModel):
    name: str
    description: str

class TaskUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


# GET - Get all tasks
@app.get("/tasks", response_model=List[Task])
def get_tasks(db: Session = Depends(get_db)):
    """
    Returns all tasks in the database
    """
    tasks = db.query(TaskModel).all()
    return tasks


# GET - Get a specific task by ID
@app.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(get_db)):
    """
    Returns a specific task by ID
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


# POST - Add a new task
@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_create: TaskCreate, db: Session = Depends(get_db)):
    """
    Creates a new task
    """
    new_task = TaskModel(name=task_create.name, description=task_create.description)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task


# PUT - Update an existing task
@app.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """
    Updates an existing task
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task_update.name is not None:
        task.name = task_update.name
    if task_update.description is not None:
        task.description = task_update.description
    
    db.commit()
    db.refresh(task)
    return task


# DELETE - Delete a task
@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    """
    Deletes a task from the database
    """
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db.delete(task)
    db.commit()


# Root endpoint
@app.get("/")
def root():
    """
    Welcome endpoint
    """
    return {"message": "Welcome to Task Manager API"}
