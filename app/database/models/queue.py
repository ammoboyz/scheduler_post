from .base import Base, bigint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime


class Queue(Base):
    __tablename__ = "queue"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        primary_key=True
    )

    message_id: Mapped[bigint] = mapped_column(
        default=0
    )

    pic_url: Mapped[str]
    prompt: Mapped[str] = mapped_column(
        default=""
    )

    is_sended: Mapped[bool] = mapped_column(
        default=False
    )

    disable_notification: Mapped[bool] = mapped_column(
        default=False
    )

    schedule_date: Mapped[datetime]
