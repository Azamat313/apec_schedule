from datetime import date

from pydantic import BaseModel, ConfigDict


class GroupOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class TeacherOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str


class RoomOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    number: str


class LessonOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    date: date
    pair_number: int
    status: str
    discipline: str
    lesson_type: str
    group: GroupOut
    teacher: TeacherOut | None
    substitute_teacher: TeacherOut | None
    room: RoomOut | None
    notes: str | None
    change_reason: str | None


class LessonIn(BaseModel):
    date: date
    pair_number: int
    discipline: str
    lesson_type: str = "theory"
    status: str = "planned"
    group_id: int
    teacher_id: int | None = None
    substitute_teacher_id: int | None = None
    room_id: int | None = None
    notes: str | None = None
    change_reason: str | None = None


class LessonPatch(BaseModel):
    status: str | None = None
    substitute_teacher_id: int | None = None
    room_id: int | None = None
    notes: str | None = None
    change_reason: str | None = None
