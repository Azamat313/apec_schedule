# Мобильные приложения (Flutter)

Два приложения на общей кодовой базе. Реализация — циклы 2–3
(см. `../docs/ARCHITECTURE.md`).

## Структура монорепо

```
mobile/
  packages/
    apec_api/    # API-клиент: генерируется из http://<backend>/openapi.json
                 # (openapi-generator, dart-dio) + хранение JWT (flutter_secure_storage)
    apec_ui/     # дизайн-система: цвета колледжа, карточка пары, календарь недели
  apps/
    student/     # «АПЭК Студент»
    teacher/     # «АПЭК Преподаватель»
```

## «АПЭК Студент» — MVP (цикл 2)

1. Вход / выбор группы (JWT из `POST /api/auth/login`)
2. Экран «Сегодня/Неделя»: `GET /api/schedule/week/{date}?group_id=…`
   - замены выделены, отменённые пары зачёркнуты (`status`, `substitute_teacher`)
3. Push о заменах: регистрация FCM-токена `POST /api/notifications/devices`,
   лента `GET /api/notifications`
4. Объявления: `GET /api/announcements`
5. Офлайн-кэш последней загруженной недели (drift/sqlite)

## «АПЭК Преподаватель» — MVP (цикл 3)

1. Вход преподавателя (учётка привязана к `teacher_id`)
2. Своё расписание: `GET /api/schedule/week/{date}?teacher_id=…`
   (включая пары, где он назначен заменой)
3. Push о своих заменах
4. Далее: электронный журнал (модуль grades), отметка посещаемости (attendance)

## Технологии

- Flutter 3.x, Dart 3
- Riverpod (состояние), dio (сеть), firebase_messaging (push)
- Один Firebase-проект на оба приложения
