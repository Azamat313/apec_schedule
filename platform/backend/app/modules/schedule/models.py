from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Group(Base):
    __tablename__ = "groups"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, index=True)


class Teacher(Base):
    __tablename__ = "teachers"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(20), unique=True)


class Lesson(Base):
    """Пара в расписании. Единица данных всей платформы:
    к ней привязываются оценки (grades) и посещаемость (attendance)."""

    __tablename__ = "lessons"
    __table_args__ = (
        UniqueConstraint("date", "pair_number", "group_id", name="uq_lesson_slot"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[date] = mapped_column(Date, index=True)
    pair_number: Mapped[int] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(20), default="planned")  # planned|done|cancelled
    discipline: Mapped[str] = mapped_column(String(200))
    lesson_type: Mapped[str] = mapped_column(String(20), default="theory")  # theory|practice|lab

    group_id: Mapped[int] = mapped_column(ForeignKey("groups.id"), index=True)
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"), index=True)
    substitute_teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"))
    room_id: Mapped[int | None] = mapped_column(ForeignKey("rooms.id"))

    notes: Mapped[str | None] = mapped_column(Text)
    change_reason: Mapped[str | None] = mapped_column(Text)

    group: Mapped[Group] = relationship(lazy="joined")
    teacher: Mapped[Teacher | None] = relationship(foreign_keys=[teacher_id], lazy="joined")
    substitute_teacher: Mapped[Teacher | None] = relationship(
        foreign_keys=[substitute_teacher_id], lazy="joined"
    )
    room: Mapped[Room | None] = relationship(lazy="joined")
