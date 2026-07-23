"""Миграция данных из старого формата (JSON-выгрузки GitHub Pages).

Разовый импорт: переносит группы, преподавателей, кабинеты и расписание
из schedule.json старого проекта в базу платформы.
"""
import json
import logging
from datetime import date
from pathlib import Path

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.modules.schedule.models import Group, Lesson, Room, Teacher

log = logging.getLogger(__name__)


def import_legacy(db: Session, data_dir: Path) -> int:
    schedule_file = data_dir / "schedule.json"
    if not schedule_file.exists():
        log.warning("Файл %s не найден — импорт пропущен", schedule_file)
        return 0

    payload = json.loads(schedule_file.read_text(encoding="utf-8"))
    entries = payload.get("schedules", [])

    groups: dict[int, Group] = {}
    teachers: dict[int, Teacher] = {}
    rooms: dict[int, Room] = {}
    imported = 0

    for entry in entries:
        g = entry["group"]
        if g["id"] not in groups:
            groups[g["id"]] = Group(id=g["id"], name=g["name"])
        teacher = entry.get("teacher")
        if teacher and teacher["id"] not in teachers:
            teachers[teacher["id"]] = Teacher(id=teacher["id"], name=teacher["name"])
        sub = entry.get("substitute_teacher")
        if sub and sub["id"] not in teachers:
            teachers[sub["id"]] = Teacher(id=sub["id"], name=sub["name"])
        room = entry.get("room")
        if room and room["id"] not in rooms:
            rooms[room["id"]] = Room(id=room["id"], number=room["number"])

    db.add_all(groups.values())
    db.add_all(teachers.values())
    db.add_all(rooms.values())
    db.flush()

    for entry in entries:
        db.add(
            Lesson(
                id=entry["id"],
                date=date.fromisoformat(entry["date"]),
                pair_number=entry["pair_number"],
                status=entry.get("status") or "planned",
                discipline=entry["discipline"],
                lesson_type=entry.get("lesson_type") or "theory",
                group_id=entry["group"]["id"],
                teacher_id=entry["teacher"]["id"] if entry.get("teacher") else None,
                substitute_teacher_id=(
                    entry["substitute_teacher"]["id"] if entry.get("substitute_teacher") else None
                ),
                room_id=entry["room"]["id"] if entry.get("room") else None,
                notes=entry.get("notes"),
                change_reason=entry.get("change_reason"),
            )
        )
        imported += 1

    db.commit()
    log.info("Импортировано %d пар, %d групп, %d преподавателей", imported, len(groups), len(teachers))
    return imported


def import_legacy_if_empty(db: Session, data_dir: Path) -> int:
    if db.scalar(select(func.count(Lesson.id))):
        return 0
    return import_legacy(db, data_dir)
