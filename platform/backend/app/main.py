import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import Base, SessionLocal, engine
from app.modules.announcements.router import router as announcements_router
from app.modules.auth.router import router as auth_router
from app.modules.notifications import service as notifications_service
from app.modules.notifications.router import router as notifications_router
from app.modules.schedule.importer import import_legacy_if_empty
from app.modules.schedule.router import router as schedule_router

logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(engine)
    notifications_service.register_handlers()
    if settings.auto_import_legacy:
        with SessionLocal() as db:
            import_legacy_if_empty(db, settings.legacy_data_dir)
    yield


app = FastAPI(
    title=settings.app_name,
    description="Модульная платформа АПЭК Петротехник: расписание, пользователи, "
    "уведомления, объявления. Клиенты: мобильные приложения (Flutter) и веб.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(schedule_router)
app.include_router(notifications_router)
app.include_router(announcements_router)


@app.get("/health", tags=["system"])
def health():
    return {"status": "ok", "app": settings.app_name}
