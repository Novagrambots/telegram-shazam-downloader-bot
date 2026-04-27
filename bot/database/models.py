"""Модели базы данных — User, Channel, ShazamRequest"""
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Базовый класс для всех моделей"""
    pass


class User(Base):
    """Пользователь бота"""
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255))
    # когда первый раз зашел в бота
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # сколько раз делал распознавания
    download_count: Mapped[int] = mapped_column(default=0)
    # язык интерфейса: ru / uz / en
    language: Mapped[str] = mapped_column(String(5), default="ru")

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.username})>"


class Channel(Base):
    """Канал/группа для обязательной подписки"""
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # id канала в Telegram (например -1001234567890)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True)
    # название для отображения юзеру
    title: Mapped[str] = mapped_column(String(255))
    # ссылка на канал (для кнопки "Подписаться")
    invite_link: Mapped[str] = mapped_column(String(255))
    # когда добавлен
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<Channel {self.channel_id} ({self.title})>"


class ShazamRequest(Base):
    """Запрос на распознавание трека через Shazam"""
    __tablename__ = "shazam_requests"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    # пользователь, который сделал запрос
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("users.telegram_id"), index=True
    )
    # тип входящего медиа: voice, audio, video, video_note
    input_type: Mapped[str] = mapped_column(String(50))
    # длина медиа в секундах (если известна)
    input_duration: Mapped[int | None] = mapped_column(Integer, nullable=True)
    # удалось ли распознать трек
    recognized: Mapped[bool] = mapped_column(Boolean, default=False)
    # название трека (если распознан)
    track_title: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # исполнитель (если распознан)
    track_artist: Mapped[str | None] = mapped_column(String(500), nullable=True)
    # ID трека в базе Shazam
    shazam_track_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
    # когда создан запрос
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    def __repr__(self) -> str:
        status = "OK" if self.recognized else "FAIL"
        return f"<ShazamRequest user={self.user_id} [{status}] {self.track_title}>"
