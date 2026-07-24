"""Справочные значения, выведенные из фактической выгрузки старой системы.

Замер по docs/api/schedule.json (19 443 записи, 12.01.2026 — 24.06.2026):
    status:      done 17437 | substitution 1055 | cancelled 837 | completed 114
    lesson_type: theory 17608 | practice 1835
    pair_number: 1..7

Замечание к данным: `completed` и `done` выглядят как два названия одного
состояния (историческое расхождение в старой системе). Импортер сводит
`completed` -> `done`; если это разные состояния, правило надо изменить.
"""

class LessonStatus:
    PLANNED = "planned"          # добавлено платформой: пара в будущем, ещё не проведена
    DONE = "done"                # проведена
    CANCELLED = "cancelled"      # отменена
    SUBSTITUTION = "substitution"  # проведена с заменой преподавателя

    ALL = (PLANNED, DONE, CANCELLED, SUBSTITUTION)


class LessonType:
    THEORY = "theory"
    PRACTICE = "practice"

    ALL = (THEORY, PRACTICE)


# Нормализация статусов из старой выгрузки в статусы платформы
LEGACY_STATUS_MAP = {
    "done": LessonStatus.DONE,
    "completed": LessonStatus.DONE,
    "cancelled": LessonStatus.CANCELLED,
    "substitution": LessonStatus.SUBSTITUTION,
}

MAX_PAIR_NUMBER = 7
