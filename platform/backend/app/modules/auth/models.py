from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(200))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[str] = mapped_column(String(20), default="student")  # student|teacher|admin

    # Привязки к доменным сущностям расписания
    group_id: Mapped[int | None] = mapped_column(ForeignKey("groups.id"))
    teacher_id: Mapped[int | None] = mapped_column(ForeignKey("teachers.id"))
