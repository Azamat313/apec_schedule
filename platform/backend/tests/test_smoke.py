"""Смоук-тесты платформы: поднимаем приложение на пустой in-memory базе
с маленьким набором данных и проверяем ключевые сценарии каждого модуля."""
import os

os.environ["APEC_DATABASE_URL"] = "sqlite://"
os.environ["APEC_AUTO_IMPORT_LEGACY"] = "false"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool

import app.core.database as database
from app.core.config import settings  # noqa: F401  (форсируем чтение env выше)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Одна shared in-memory SQLite на все сессии
database.engine = create_engine(
    "sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
database.SessionLocal = sessionmaker(bind=database.engine, expire_on_commit=False)

from app.main import app  # noqa: E402
import app.main as main_module  # noqa: E402

main_module.engine = database.engine
main_module.SessionLocal = database.SessionLocal


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def admin_token(client):
    client.post(
        "/api/auth/register",
        json={
            "email": "admin@apec.edu.kz",
            "password": "secret123",
            "full_name": "Администратор",
            "role": "admin",
        },
    )
    resp = client.post(
        "/api/auth/login",
        data={"username": "admin@apec.edu.kz", "password": "secret123"},
    )
    return resp.json()["access_token"]


def auth(token):
    return {"Authorization": f"Bearer {token}"}


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_schedule_crud_and_notifications(client, admin_token):
    # Справочники создаём напрямую через сессию (админ-CRUD справочников — цикл 1)
    from app.modules.schedule.models import Group, Room, Teacher

    with database.SessionLocal() as db:
        db.add_all([
            Group(id=1, name="АиУ 1-25"),
            Teacher(id=1, name="Абсенова Б."),
            Room(id=1, number="105"),
        ])
        db.commit()

    # Студент группы 1 — получатель уведомлений
    client.post(
        "/api/auth/register",
        json={
            "email": "student@apec.edu.kz",
            "password": "secret123",
            "full_name": "Студент",
            "role": "student",
            "group_id": 1,
        },
    )
    student_token = client.post(
        "/api/auth/login",
        data={"username": "student@apec.edu.kz", "password": "secret123"},
    ).json()["access_token"]

    # Без прав админа пара не создаётся
    lesson = {
        "date": "2026-09-01", "pair_number": 1, "discipline": "Физика",
        "group_id": 1, "teacher_id": 1, "room_id": 1,
    }
    assert client.post("/api/schedule", json=lesson, headers=auth(student_token)).status_code == 403

    # Админ создаёт пару
    resp = client.post("/api/schedule", json=lesson, headers=auth(admin_token))
    assert resp.status_code == 200, resp.text
    lesson_id = resp.json()["id"]

    # Пара видна в выборках
    day = client.get("/api/schedule/day/2026-09-01", params={"group_id": 1}).json()
    assert len(day) == 1 and day[0]["discipline"] == "Физика"
    week = client.get("/api/schedule/week/2026-09-03", params={"group_id": 1}).json()
    assert len(week) == 1

    # Отмена пары -> студенту группы приходит уведомление
    resp = client.patch(
        f"/api/schedule/{lesson_id}",
        json={"status": "cancelled", "change_reason": "Болезнь преподавателя"},
        headers=auth(admin_token),
    )
    assert resp.json()["status"] == "cancelled"

    notifications = client.get("/api/notifications", headers=auth(student_token)).json()
    assert any("отменена" in n["title"] for n in notifications)


def test_announcements(client, admin_token):
    resp = client.post(
        "/api/announcements",
        json={"title": "Собрание", "body": "Актовый зал, 15:00", "audience": "all"},
        headers=auth(admin_token),
    )
    assert resp.status_code == 201
    feed = client.get("/api/announcements", headers=auth(admin_token)).json()
    assert any(a["title"] == "Собрание" for a in feed)


def test_legacy_importer(tmp_path):
    import json

    from app.modules.schedule.importer import import_legacy

    payload = {
        "schedules": [
            {
                "id": 100, "date": "2026-01-12", "pair_number": 1, "status": "done",
                "discipline": "Английский язык", "lesson_type": "theory",
                "group": {"id": 17, "name": "БНГС 1-25"},
                "teacher": {"id": 10, "name": "Аяпбергенова О."},
                "substitute_teacher": None,
                "room": {"id": 29, "number": "209"},
                "notes": None, "change_reason": None,
            }
        ]
    }
    (tmp_path / "schedule.json").write_text(json.dumps(payload), encoding="utf-8")
    with database.SessionLocal() as db:
        assert import_legacy(db, tmp_path) == 1
