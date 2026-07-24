"""Уведомления: подписка на события расписания.

При замене/отмене пары создаются уведомления студентам группы и
затронутым преподавателям. Отправка в FCM — точка расширения send_push().
"""
import logging

from sqlalchemy import select

from app.core import events
from app.core.database import SessionLocal
from app.modules.auth.models import User
from app.modules.notifications.models import Notification

log = logging.getLogger(__name__)

_CHANGE_TITLES = {
    "created": "Новая пара",
    "updated": "Изменение в расписании",
    "cancelled": "Пара отменена",
    "substitution": "Замена преподавателя",
    "room_changed": "Изменение кабинета",
}


def send_push(user_id: int, title: str, body: str) -> None:
    # Точка интеграции с Firebase Cloud Messaging (цикл 2):
    # выбрать DeviceToken пользователя и отправить через firebase-admin.
    log.info("push -> user %s: %s", user_id, title)


def on_schedule_changed(lesson, change: str, **_) -> None:
    title = _CHANGE_TITLES.get(change, "Изменение в расписании")
    body = (
        f"{lesson.date} пара {lesson.pair_number}: {lesson.discipline} "
        f"({lesson.group.name})"
    )
    if change == "substitution" and lesson.substitute_teacher:
        body += f" — ведёт {lesson.substitute_teacher.name}"
    elif change == "room_changed" and lesson.room:
        body += f" — кабинет {lesson.room.number}"
    if lesson.change_reason:
        body += f" — {lesson.change_reason}"

    with SessionLocal() as db:
        affected = db.scalars(
            select(User).where(
                (User.group_id == lesson.group_id)
                | (User.teacher_id.in_([t for t in (lesson.teacher_id, lesson.substitute_teacher_id) if t]))
            )
        )
        for user in affected:
            db.add(Notification(user_id=user.id, title=title, body=body, kind="schedule"))
            send_push(user.id, title, body)
        db.commit()


def register_handlers() -> None:
    events.subscribe("schedule_changed", on_schedule_changed)
