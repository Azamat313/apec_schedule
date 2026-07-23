# АПЭК Digital — платформа колледжа

Модульная платформа АПЭК Петротехник: расписание, пользователи, уведомления,
объявления + мобильные приложения (Flutter). Архитектура и план развития —
в [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

> Эта папка — корень будущего нового репозитория `apec-platform`.
> Старый репозиторий `apec_schedule` (GitHub Pages) не изменяется.

## Быстрый старт (разработка)

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

- Swagger UI: http://localhost:8000/docs
- При первом запуске данные автоматически импортируются из старых
  JSON-выгрузок (`docs/api/schedule.json` старого репозитория) — 19 443 пары,
  78 групп, 76 преподавателей.

## Запуск в проде

```bash
APEC_SECRET_KEY=<случайный-ключ> docker compose up -d --build
```

Поднимает backend + PostgreSQL. Перед прод-запуском обязательно задайте
`APEC_SECRET_KEY`.

## Тесты

```bash
cd backend
pip install pytest httpx
python -m pytest tests/ -v
```

## Структура

```
platform/
  docs/ARCHITECTURE.md   # архитектура, модули, циклы разработки
  backend/
    app/
      core/              # конфиг, БД, безопасность, шина событий
      modules/
        schedule/        # расписание (ядро) — модели, API, импортер
        auth/            # пользователи, роли, JWT
        notifications/   # уведомления + push (FCM)
        announcements/   # новости и объявления
    tests/
  mobile/                # план мобильных приложений (Flutter)
  docker-compose.yml
```

## Первый администратор

Пока нет ни одного администратора, его можно создать открытой регистрацией:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@apec.edu.kz","password":"...","full_name":"Диспетчер","role":"admin"}'
```

После появления первого админа открытая регистрация админов закрывается.
