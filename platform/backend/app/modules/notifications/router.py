from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.modules.auth.models import User
from app.modules.notifications.models import DeviceToken, Notification

router = APIRouter(prefix="/api/notifications", tags=["notifications"])


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    body: str
    kind: str
    created_at: datetime
    read_at: datetime | None


class DeviceIn(BaseModel):
    token: str
    platform: str = "android"


@router.get("", response_model=list[NotificationOut])
def my_notifications(
    unread_only: bool = False,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    q = (
        select(Notification)
        .where(Notification.user_id == user.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
    )
    if unread_only:
        q = q.where(Notification.read_at.is_(None))
    return list(db.scalars(q))


@router.post("/{notification_id}/read", response_model=NotificationOut)
def mark_read(
    notification_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notif = db.get(Notification, notification_id)
    if notif is None or notif.user_id != user.id:
        raise HTTPException(status_code=404, detail="Уведомление не найдено")
    notif.read_at = datetime.now(timezone.utc)
    db.commit()
    return notif


@router.post("/devices", status_code=201)
def register_device(
    data: DeviceIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.scalar(select(DeviceToken).where(DeviceToken.token == data.token))
    if existing:
        existing.user_id = user.id
        existing.platform = data.platform
    else:
        db.add(DeviceToken(user_id=user.id, token=data.token, platform=data.platform))
    db.commit()
    return {"status": "ok"}
