"""Скачивание аудио-дорожки трека с YouTube через yt-dlp.

Используется ПОСЛЕ распознавания: если у Shazam пришла YouTube-ссылка —
качаем её, иначе — поиск по "{artist} - {title}" через ytsearch1.

Качаем ТОЛЬКО аудио-стрим (DASH) в нативном формате — m4a/AAC. Перекодирования нет.
Telegram нативно играет m4a через send_audio.
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from dataclasses import dataclass

import yt_dlp

from bot.config import settings

logger = logging.getLogger(__name__)

# семафор на параллельные скачивания, чтобы не перегружать сервер
_download_semaphore = asyncio.Semaphore(2)

# лимит длительности — отсекаем подкасты/часовые миксы (берём только треки)
_MAX_DURATION_SEC = 15 * 60  # 15 минут

# WARP контейнер из docker-compose
_WARP_PROXY = "socks5://warp:9091"


class TrackDownloadError(Exception):
    """Не удалось скачать трек (yt-dlp упал, лимит превышен, и т.д.)."""


@dataclass
class DownloadedTrack:
    file_path: str
    ext: str          # m4a / webm / opus
    duration: int     # секунды
    title: str
    artist: str


def _ydl_opts(output_template: str, proxy: str | None = None) -> dict:
    opts = {
        # m4a приоритет (нативный AAC от YouTube), webm/opus как fallback
        "format": "bestaudio[ext=m4a]/bestaudio",
        "outtmpl": output_template,
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
        "nocheckcertificate": True,
        "concurrent_fragment_downloads": 4,
        # подрезаем по длительности
        "match_filter": yt_dlp.utils.match_filter_func(f"duration < {_MAX_DURATION_SEC}"),
    }
    if proxy:
        opts["proxy"] = proxy
    return opts


def _build_attempts() -> list[tuple[str, str | None]]:
    """
    Цепочка попыток: residential SOCKS5 → WARP → direct.
    Каждый элемент: (имя_для_логов, proxy_url или None для прямого подключения).
    """
    attempts: list[tuple[str, str | None]] = []
    if settings.proxy_url:
        attempts.append(("residential-proxy", settings.proxy_url))
    attempts.append(("warp", _WARP_PROXY))
    attempts.append(("direct", None))
    return attempts


def _download_sync(query: str, output_dir: str, proxy: str | None) -> DownloadedTrack:
    """Синхронный yt-dlp в отдельном потоке (вызывается через asyncio.to_thread)."""
    output_template = os.path.join(output_dir, "%(id)s.%(ext)s")
    opts = _ydl_opts(output_template, proxy=proxy)

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(query, download=True)

    # для ytsearch результат — это dict со списком entries
    if info.get("_type") == "playlist" or "entries" in info:
        entries = info.get("entries") or []
        if not entries:
            raise TrackDownloadError("yt-dlp вернул пустой список результатов")
        info = entries[0]

    if not info:
        raise TrackDownloadError("yt-dlp не вернул данных")

    file_path = ydl.prepare_filename(info)
    if not os.path.exists(file_path):
        # иногда расширение в filename отличается от реального ext
        actual_ext = info.get("ext", "m4a")
        file_path = os.path.splitext(file_path)[0] + f".{actual_ext}"

    if not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
        raise TrackDownloadError(f"файл не создан: {file_path}")

    return DownloadedTrack(
        file_path=file_path,
        ext=info.get("ext", "m4a"),
        duration=int(info.get("duration") or 0),
        title=info.get("title") or "",
        artist=info.get("uploader") or "",
    )


async def download_track(
    *,
    youtube_url: str | None,
    title: str,
    artist: str,
    output_dir: str,
) -> DownloadedTrack:
    """
    Скачивает аудио. Сначала пробует прямой YouTube-URL (если передан),
    иначе делает поиск по "artist - title".

    Бросает TrackDownloadError при любых сбоях.
    """
    # сначала пробуем прямой URL (если он был от Shazam),
    # потом fallback — поиск по "artist - title"
    queries: list[tuple[str, str]] = []
    if youtube_url:
        queries.append(("direct-url", youtube_url))
    queries.append(("search", f"ytsearch1:{artist} - {title} audio"))

    attempts = _build_attempts()
    last_exc: Exception | None = None

    async with _download_semaphore:
        for q_name, query in queries:
            logger.info("Track download via %s: %s", q_name, query)
            for name, proxy in attempts:
                try:
                    logger.info("  attempt: %s", name)
                    return await asyncio.to_thread(
                        _download_sync, query, output_dir, proxy
                    )
                except (yt_dlp.utils.DownloadError, TrackDownloadError) as exc:
                    last_exc = exc
                    logger.warning(
                        "yt-dlp [%s/%s] failed: %s", q_name, name, exc
                    )
                    continue
                except Exception as exc:
                    last_exc = exc
                    logger.warning(
                        "yt-dlp [%s/%s] unexpected: %s", q_name, name, exc
                    )
                    continue

    raise TrackDownloadError(f"all download attempts failed: {last_exc}")
