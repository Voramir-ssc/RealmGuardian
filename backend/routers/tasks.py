from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import pydantic
import models
from dependencies import get_db

router = APIRouter(prefix="/api/user/tasks", tags=["Tasks"])

class TaskCreate(pydantic.BaseModel):
    title: str
    type: str # 'daily', 'weekly', 'monthly', 'manual'

class TaskUpdate(pydantic.BaseModel):
    is_completed: bool

@router.get('')
def get_user_tasks(db: Session = Depends(get_db)):
    """Retrieves all user tasks, ordered by type and creation date."""
    tasks = db.query(models.UserTask).order_by(models.UserTask.type, models.UserTask.created_at.desc()).all()
    return {"tasks": tasks}

@router.post('')
def create_user_task(task: TaskCreate, db: Session = Depends(get_db)):
    """Creates a new user task."""
    db_task = models.UserTask(title=task.title, type=task.type)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.put('/{task_id}')
def update_user_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    """Updates a task's completion status."""
    db_task = db.query(models.UserTask).filter(models.UserTask.id == task_id).first()
    if not db_task: raise HTTPException(status_code=404, detail="Task not found")
        
    db_task.is_completed = task_update.is_completed
    if task_update.is_completed:
        db_task.last_completed_at = datetime.utcnow()
    else:
        db_task.last_completed_at = None
        
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete('/{task_id}')
def delete_user_task(task_id: int, db: Session = Depends(get_db)):
    """Deletes a user task."""
    db_task = db.query(models.UserTask).filter(models.UserTask.id == task_id).first()
    if not db_task: raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"message": "Task deleted"}
