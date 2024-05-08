from .base import Base, bigint
from sqlalchemy.orm import Mapped, mapped_column


class Config(Base):
    __tablename__ = "config"

    id: Mapped[int] = mapped_column(
        autoincrement=True,
        primary_key=True
    )

    channel_id: Mapped[bigint] = mapped_column(
        default=0
    )

    description: Mapped[str] = mapped_column(
        default=""
    )

    gup_minutes: Mapped[int] = mapped_column(
        default=30
    )
