from datetime import date, timedelta

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core import events
from app.modules.schedule.models import Group, Lesson, Room, Teacher
from app.modules.schedule.schemas import LessonIn, LessonPatch


def list_lessons(
    db: Session,
    group_id: int | None = None,
    teacher_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    limit: int = 500,
    offset: int = 0,
) -> list[Lesson]:
    q = select(Lesson).order_by(Lesson.date, Lesson.pair_number)
    if group_id:
        q = q.where(Lesson.group_id == group_id)
    if teacher_id:
        q = q.where(
            (Lesson.teacher_id == teacher_id) | (Lesson.substitute_teacher_id == teacher_id)
        )
    if date_from:
        q = q.where(Lesson.date >= date_from)
    if date_to:
        q = q.where(Lesson.date <= date_to)
    if status:
        q = q.where(Lesson.status == status)
    return list(db.scalars(q.limit(limit).offset(offset)))


def week_bounds(day: date) -> tuple[date, date]:
    start = day - timedelta(days=day.weekday())
    return start, start + timedelta(days=6)


def create_lesson(db: Session, data: LessonIn) -> Lesson:
    lesson = Lesson(**data.model_dump())
    db.add(lesson)
    db.commit()
    events.publish("schedule_changed", lesson=lesson, change="created")
    return lesson


def update_lesson(db: Session, lesson_id: int, patch: LessonPatch) -> Lesson:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Пара не найдена")
    changes = patch.model_dump(exclude_unset=True)
    for field, value in changes.items():
        setattr(lesson, field, value)
    db.commit()
    change = "cancelled" if changes.get("status") == "cancelled" else "updated"
    events.publish("schedule_changed", lesson=lesson, change=change)
    return lesson


def delete_lesson(db: Session, lesson_id: int) -> None:
    lesson = db.get(Lesson, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Пара не найдена")
    db.delete(lesson)
    db.commit()


def list_groups(db: Session) -> list[Group]:
    return list(db.scalars(select(Group).order_by(Group.name)))


def list_teachers(db: Session) -> list[Teacher]:
    return list(db.scalars(select(Teacher).order_by(Teacher.name)))


def list_rooms(db: Session) -> list[Room]:
    return list(db.scalars(select(Room).order_by(Room.number)))
