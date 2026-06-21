from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from pydantic import BaseModel

from backend.core.database import get_db
from backend.models.user import User, UserGoal, SkillLevel, GoalStatus

router = APIRouter(prefix="/users", tags=["users"])


class UserCreate(BaseModel):
    username: str
    display_name: str = ""
    email: str = ""
    skill_level: str = "intermediate"
    preferences: Dict[str, Any] = {}


class UserUpdate(BaseModel):
    display_name: str = ""
    email: str = ""
    skill_level: str = ""
    preferences: Dict[str, Any] = {}


class GoalCreate(BaseModel):
    title: str
    description: str = ""
    domain: str = "general"
    target_date: str = ""


@router.get("")
async def list_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    return {
        "users": [{"id": u.id, "username": u.username, "display_name": u.display_name,
                    "role": u.role, "skill_level": u.skill_level.value,
                    "is_active": u.is_active, "created_at": u.created_at.isoformat()}
                  for u in users]
    }


@router.post("", status_code=201)
async def create_user(data: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == data.username).first()
    if existing:
        raise HTTPException(status_code=409, detail="Username already exists")
    user = User(
        username=data.username,
        display_name=data.display_name or data.username,
        email=data.email,
        skill_level=SkillLevel(data.skill_level) if data.skill_level else SkillLevel.INTERMEDIATE,
        preferences=data.preferences,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"id": user.id, "username": user.username, "skill_level": user.skill_level.value}


@router.get("/{user_id}")
async def get_user(user_id: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return {
        "id": user.id, "username": user.username, "display_name": user.display_name,
        "email": user.email, "role": user.role, "skill_level": user.skill_level.value,
        "preferences": user.preferences or {},
        "is_active": user.is_active,
        "created_at": user.created_at.isoformat(),
    }


@router.patch("/{user_id}")
async def update_user(user_id: str, data: UserUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    if data.display_name:
        user.display_name = data.display_name
    if data.email:
        user.email = data.email
    if data.skill_level:
        user.skill_level = SkillLevel(data.skill_level)
    if data.preferences:
        user.preferences = {**(user.preferences or {}), **data.preferences}
    db.commit()
    return {"status": "updated", "user_id": user_id}


@router.get("/{user_id}/goals")
async def list_goals(user_id: str, db: Session = Depends(get_db)):
    goals = db.query(UserGoal).filter(UserGoal.user_id == user_id).all()
    return {
        "goals": [{"id": g.id, "title": g.title, "domain": g.domain,
                    "status": g.status.value, "progress": g.progress,
                    "target_date": g.target_date, "created_at": g.created_at.isoformat()}
                  for g in goals]
    }


@router.post("/{user_id}/goals", status_code=201)
async def create_goal(user_id: str, data: GoalCreate, db: Session = Depends(get_db)):
    goal = UserGoal(user_id=user_id, title=data.title, description=data.description,
                    domain=data.domain, target_date=data.target_date)
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return {"id": goal.id, "title": goal.title, "status": goal.status.value}


@router.patch("/{user_id}/goals/{goal_id}")
async def update_goal(user_id: str, goal_id: str, data: Dict[str, Any],
                      db: Session = Depends(get_db)):
    goal = db.query(UserGoal).filter(UserGoal.id == goal_id, UserGoal.user_id == user_id).first()
    if not goal:
        raise HTTPException(404, "Goal not found")
    if "status" in data:
        goal.status = GoalStatus(data["status"])
    if "progress" in data:
        goal.progress = int(data["progress"])
    if "title" in data:
        goal.title = data["title"]
    db.commit()
    return {"status": "updated", "goal_id": goal_id}
