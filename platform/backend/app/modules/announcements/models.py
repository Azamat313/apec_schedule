from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Announcement(Base):
    __tablename__ = "announcements"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    body: Mapped[str] = mapped_column(Text)
    # Аудитория: all — все, students — студенты, teachers — преподаватели,
    # group — конкретная группа (target_group_id)
    audience: Mapped[str] = mapped_column(String(20), default="all")
    target_group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
