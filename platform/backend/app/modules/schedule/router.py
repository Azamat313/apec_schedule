from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import require_role
from app.modules.schedule import service
from app.modules.schedule.schemas import (
    GroupOut,
    LessonIn,
    LessonOut,
    LessonPatch,
    RoomOut,
    TeacherOut,
)

router = APIRouter(prefix="/api", tags=["schedule"])


@router.get("/schedule", response_model=list[LessonOut])
def get_schedule(
    group_id: int | None = None,
    teacher_id: int | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    status: str | None = None,
    limit: int = 500,
    offset: int = 0,
    db: Session = Depends(get_db),
):
    return service.list_lessons(db, group_id, teacher_id, date_from, date_to, status, limit, offset)


@router.get("/schedule/day/{day}", response_model=list[LessonOut])
def get_day(day: date, group_id: int | None = None, teacher_id: int | None = None,
            db: Session = Depends(get_db)):
    return service.list_lessons(db, group_id, teacher_id, date_from=day, date_to=day)


@router.get("/schedule/week/{day}", response_model=list[LessonOut])
def get_week(day: date, group_id: int | None = None, teacher_id: int | None = None,
             db: Session = Depends(get_db)):
    start, end = service.week_bounds(day)
    return service.list_lessons(db, group_id, teacher_id, date_from=start, date_to=end)


@router.post("/schedule", response_model=LessonOut,
             dependencies=[Depends(require_role("admin"))])
def create_lesson(data: LessonIn, db: Session = Depends(get_db)):
    return service.create_lesson(db, data)


@router.patch("/schedule/{lesson_id}", response_model=LessonOut,
              dependencies=[Depends(require_role("admin"))])
def update_lesson(lesson_id: int, patch: LessonPatch, db: Session = Depends(get_db)):
    return service.update_lesson(db, lesson_id, patch)


@router.delete("/schedule/{lesson_id}", status_code=204,
               dependencies=[Depends(require_role("admin"))])
def delete_lesson(lesson_id: int, db: Session = Depends(get_db)):
    service.delete_lesson(db, lesson_id)


@router.get("/groups", response_model=list[GroupOut])
def get_groups(db: Session = Depends(get_db)):
    return service.list_groups(db)


@router.get("/teachers", response_model=list[TeacherOut])
def get_teachers(db: Session = Depends(get_db)):
    return service.list_teachers(db)


@router.get("/rooms", response_model=list[RoomOut])
def get_rooms(db: Session = Depends(get_db)):
    return service.list_rooms(db)
