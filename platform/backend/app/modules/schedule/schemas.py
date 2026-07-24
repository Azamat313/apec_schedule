from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from app.modules.schedule.constants import MAX_PAIR_NUMBER

LessonStatusLiteral = Literal["planned", "done", "cancelled", "substitution"]
LessonTypeLiteral = Literal["theory", "practice"]


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
    pair_number: int = Field(ge=1, le=MAX_PAIR_NUMBER)
    discipline: str
    lesson_type: LessonTypeLiteral = "theory"
    status: LessonStatusLiteral = "planned"
    group_id: int
    teacher_id: int | None = None
    substitute_teacher_id: int | None = None
    room_id: int | None = None
    notes: str | None = None
    change_reason: str | None = None


class LessonPatch(BaseModel):
    status: LessonStatusLiteral | None = None
    substitute_teacher_id: int | None = None
    room_id: int | None = None
    notes: str | None = None
    change_reason: str | None = None
