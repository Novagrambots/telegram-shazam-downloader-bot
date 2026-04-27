"""CRUD операции с базой данных"""
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.database.models import Channel, ShazamRequest, User


async def get_or_create_user(
    session: AsyncSession,
    telegram_id: int,
    username: str | None,
    full_name: str,
    language: str | None = None,
) -> User:
    """Получить юзера или создать нового"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()

    if user is None:
        user = User(
            telegram_id=telegram_id,
            username=username,
            full_name=full_name,
            language=language or "ru",
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

    return user


async def get_user_language(session: AsyncSession, telegram_id: int) -> str:
    """Получить язык юзера (по умолчанию ru)"""
    result = await session.execute(
        select(User.language).where(User.telegram_id == telegram_id)
    )
    lang = result.scalar_one_or_none()
    return lang or "ru"


async def update_user_language(
    session: AsyncSession, telegram_id: int, language: str
) -> None:
    """Обновить язык юзера"""
    result = await session.execute(
        select(User).where(User.telegram_id == telegram_id)
    )
    user = result.scalar_one_or_none()
    if user:
        user.language = language
        await session.commit()


async def get_active_channels(session: AsyncSession) -> list[Channel]:
    """Получить все каналы для обязательной подписки"""
    result = await session.execute(select(Channel))
    return list(result.scalars().all())


async def add_channel(
    session: AsyncSession,
    channel_id: int,
    title: str,
    invite_link: str,
) -> Channel:
    """Добавить канал для обязательной подписки"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise ValueError(f"Канал {channel_id} уже добавлен")

    channel = Channel(
        channel_id=channel_id,
        title=title,
        invite_link=invite_link,
    )
    session.add(channel)
    await session.commit()
    await session.refresh(channel)
    return channel


async def remove_channel(session: AsyncSession, channel_id: int) -> bool:
    """Удалить канал. Возвращает True если удалён"""
    result = await session.execute(
        select(Channel).where(Channel.channel_id == channel_id)
    )
    channel = result.scalar_one_or_none()
    if not channel:
        return False

    await session.delete(channel)
    await session.commit()
    return True


async def get_user_stats(session: AsyncSession) -> dict:
    """Статистика: всего юзеров, за сегодня, распознаваний, каналов"""
    from sqlalchemy import func as sa_func

    total = await session.execute(select(sa_func.count(User.id)))
    total_users = total.scalar() or 0

    today = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_result = await session.execute(
        select(sa_func.count(User.id)).where(User.created_at >= today)
    )
    today_users = today_result.scalar() or 0

    downloads = await session.execute(
        select(sa_func.sum(User.download_count))
    )
    total_downloads = downloads.scalar() or 0

    channels = await session.execute(select(sa_func.count(Channel.id)))
    total_channels = channels.scalar() or 0

    return {
        "total_users": total_users,
        "today_users": today_users,
        "total_downloads": total_downloads,
        "total_channels": total_channels,
    }


async def get_all_user_ids(session: AsyncSession) -> list[int]:
    """Получить все telegram_id юзеров для рассылки"""
    result = await session.execute(select(User.telegram_id))
    return [row[0] for row in result.all()]


async def log_shazam_request(
    session: AsyncSession,
    user_id: int,
    input_type: str,
    input_duration: int | None,
    recognized: bool,
    track_title: str | None = None,
    track_artist: str | None = None,
    shazam_track_id: str | None = None,
) -> ShazamRequest:
    """Записывает запрос на распознавание и инкрементит счётчик юзера при успехе."""
    req = ShazamRequest(
        user_id=user_id,
        input_type=input_type,
        input_duration=input_duration,
        recognized=recognized,
        track_title=track_title,
        track_artist=track_artist,
        shazam_track_id=shazam_track_id,
    )
    session.add(req)

    if recognized:
        result = await session.execute(
            select(User).where(User.telegram_id == user_id)
        )
        user = result.scalar_one_or_none()
        if user:
            user.download_count = (user.download_count or 0) + 1

    await session.commit()
    await session.refresh(req)
    return req


async def get_shazam_stats(session: AsyncSession) -> dict:
    """Статистика по распознаваниям: total / recognized / failed."""
    from sqlalchemy import func as sa_func

    total_res = await session.execute(select(sa_func.count(ShazamRequest.id)))
    total = total_res.scalar() or 0

    rec_res = await session.execute(
        select(sa_func.count(ShazamRequest.id)).where(ShazamRequest.recognized.is_(True))
    )
    recognized = rec_res.scalar() or 0

    failed = total - recognized

    return {
        "total": total,
        "recognized": recognized,
        "failed": failed,
    }


async def get_top_tracks(
    session: AsyncSession, limit: int = 10
) -> list[tuple[str, str, int]]:
    """Топ распознанных треков: [(title, artist, count), ...]."""
    from sqlalchemy import func as sa_func

    stmt = (
        select(
            ShazamRequest.track_title,
            ShazamRequest.track_artist,
            sa_func.count(ShazamRequest.id).label("cnt"),
        )
        .where(ShazamRequest.recognized.is_(True))
        .where(ShazamRequest.track_title.is_not(None))
        .group_by(ShazamRequest.track_title, ShazamRequest.track_artist)
        .order_by(sa_func.count(ShazamRequest.id).desc())
        .limit(limit)
    )
    result = await session.execute(stmt)
    return [(row[0], row[1], row[2]) for row in result.all()]
