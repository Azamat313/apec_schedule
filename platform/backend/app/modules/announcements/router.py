from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel, ConfigDict
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user, require_role
from app.modules.announcements.models import Announcement
from app.modules.auth.models import User

router = APIRouter(prefix="/api/announcements", tags=["announcements"])


class AnnouncementIn(BaseModel):
    title: str
    body: str
    audience: str = "all"
    target_group_id: int | None = None


class AnnouncementOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    body: str
    audience: str
    target_group_id: int | None
    created_at: datetime


@router.get("", response_model=list[AnnouncementOut])
def list_announcements(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    conditions = [Announcement.audience == "all"]
    if user.role == "student":
        conditions.append(Announcement.audience == "students")
        if user.group_id:
            conditions.append(
                (Announcement.audience == "group")
                & (Announcement.target_group_id == user.group_id)
            )
    elif user.role == "teacher":
        conditions.append(Announcement.audience == "teachers")
    else:  # admin видит всё
        conditions = [Announcement.id.isnot(None)]
    q = select(Announcement).where(or_(*conditions)).order_by(Announcement.created_at.desc()).limit(100)
    return list(db.scalars(q))


@router.post("", response_model=AnnouncementOut, status_code=201)
def create_announcement(
    data: AnnouncementIn,
    user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    ann = Announcement(**data.model_dump(), author_id=user.id)
    db.add(ann)
    db.commit()
    return ann
