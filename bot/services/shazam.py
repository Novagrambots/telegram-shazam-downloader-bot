"""Сервис распознавания музыки через shazamio.

Архитектура:
  - extract_sample(): нарезает фрагмент входного файла в моно WAV 16kHz через ffmpeg.
  - recognize_audio(): пробует распознать трек по двум офсетам (5с и 30с), с retry на сетевые ошибки.
  - parse_track(): извлекает поля и ссылки из ответа Shazam.

Семафор ограничивает параллельные распознавания, чтобы не упереться в API.
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import tempfile
from typing import Any

import aiohttp
from shazamio import Shazam

logger = logging.getLogger(__name__)

# семафор на параллельные распознавания (модульный уровень)
_recognize_semaphore = asyncio.Semaphore(3)

# Shazam-клиент создаём один раз на уровне модуля (внутри нет состояния запроса)
_shazam = Shazam()

# минимальный размер валидного wav-сэмпла в байтах (если меньше — ffmpeg ничего не нарезал)
_MIN_SAMPLE_BYTES = 1024


# === Кастомные исключения ===

class NoAudioError(Exception):
    """В файле нет аудиодорожки."""


class ShazamServiceError(Exception):
    """Сервис Shazam недоступен после исчерпания retry."""


# === FFprobe: проверка наличия аудиодорожки ===

async def _probe(input_path: str) -> tuple[bool, float]:
    """
    Через ffprobe возвращает (есть_ли_аудио, длительность_в_секундах).

    Длительность берём из format (надёжнее, чем у потока). Если не удалось — 0.0.
    """
    cmd = [
        "ffprobe", "-i", input_path,
        "-show_streams", "-select_streams", "a",
        "-show_format",
        "-loglevel", "error",
        "-of", "json",
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout_bytes, stderr_bytes = await proc.communicate()

    if proc.returncode != 0:
        logger.warning(
            "ffprobe failed (rc=%s): %s",
            proc.returncode,
            stderr_bytes.decode("utf-8", errors="ignore").strip(),
        )
        return False, 0.0

    try:
        data = json.loads(stdout_bytes.decode("utf-8", errors="ignore") or "{}")
    except json.JSONDecodeError:
        return False, 0.0

    streams = data.get("streams") or []
    has_audio = bool(streams)

    duration = 0.0
    fmt = data.get("format") or {}
    dur_str = fmt.get("duration")
    if dur_str:
        try:
            duration = float(dur_str)
        except (TypeError, ValueError):
            duration = 0.0
    if duration == 0.0 and streams:
        s_dur = streams[0].get("duration")
        if s_dur:
            try:
                duration = float(s_dur)
            except (TypeError, ValueError):
                duration = 0.0

    return has_audio, duration


# === FFmpeg: извлечение сэмпла ===

async def extract_sample(
    input_path: str,
    output_path: str,
    offset: int,
    duration: int,
) -> bool:
    """
    Нарезает фрагмент аудио из входного файла через ffmpeg.

    Возвращает:
        True  — сэмпл успешно создан.
        False — ошибка ffmpeg или сэмпл пустой (например, файл короче offset).
    """
    # -ss ПОСЛЕ -i — output seek (точный, декодирует от начала, но гарантированно не выходит за длину)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_path,
        "-ss", str(offset),
        "-t", str(duration),
        "-ac", "1",
        "-ar", "16000",
        "-vn",
        "-loglevel", "error",
        output_path,
    ]

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    _, stderr_bytes = await proc.communicate()
    stderr = stderr_bytes.decode("utf-8", errors="ignore")

    if proc.returncode != 0:
        logger.warning("ffmpeg failed (rc=%s): %s", proc.returncode, stderr.strip())
        return False

    # доп.проверка: файл создался и не пустой
    if not os.path.exists(output_path) or os.path.getsize(output_path) < _MIN_SAMPLE_BYTES:
        logger.warning("ffmpeg sample empty/missing: %s", output_path)
        return False

    return True


# === Внутренний помощник: одна попытка распознать сэмпл ===

async def _recognize_sample(sample_path: str, retries: int = 2) -> dict | None:
    """
    Запрашивает Shazam с retry на сетевых ошибках.

    Бросает ShazamServiceError если все попытки упали с сетевой ошибкой.
    Любые другие исключения — пробрасываются наверх как есть.
    Возвращает None если Shazam отдал валидный ответ без матча.
    """
    last_exc: Exception | None = None
    attempts = retries + 1  # всего попыток

    for attempt in range(1, attempts + 1):
        try:
            return await _shazam.recognize(sample_path)
        except (
            aiohttp.ClientError,
            asyncio.TimeoutError,
            OSError,
        ) as exc:
            last_exc = exc
            logger.warning(
                "Shazam network error (attempt %d/%d): %s",
                attempt, attempts, exc,
            )
            if attempt < attempts:
                await asyncio.sleep(1)

    raise ShazamServiceError(f"Shazam unreachable: {last_exc}")


# === Публичный API: распознавание трека ===

async def recognize_audio(
    file_path: str,
    duration: int = 15,
) -> dict | None:
    """
    Пытается распознать трек, нарезая два сэмпла по офсетам [5, 30] сек.

    Возвращает:
        dict с полями track из ответа Shazam — если распознано.
        None — если оба фрагмента не дали матча.

    Бросает:
        NoAudioError      — если в файле вообще нет аудиодорожки.
        ShazamServiceError — если все попытки к Shazam упали.
    """
    has_audio, total_duration = await _probe(file_path)
    if not has_audio:
        raise NoAudioError("В файле нет аудиодорожки")

    # подбираем offset'ы адаптивно — голосовые/короткие фрагменты часто < 30 сек
    candidates = [5, 30, 60]
    offsets: list[int] = []
    if total_duration > 0:
        for o in candidates:
            # нужен хотя бы 1 секунда аудио после offset, чтобы Shazam успел матчить
            if o + 1 <= total_duration:
                offsets.append(o)
        # для очень коротких файлов всегда пробуем с самого начала
        if total_duration < 10 or not offsets:
            offsets.insert(0, 0)
    else:
        # длительность не определилась — пробуем как раньше + 0 на всякий случай
        offsets = [0, 5, 30]

    logger.info(
        "Shazam recognize: duration=%.1fs, offsets=%s",
        total_duration, offsets,
    )

    async with _recognize_semaphore:
        with tempfile.TemporaryDirectory(prefix="shazam_", dir="/tmp/shazam_bot") as tmpdir:
            for offset in offsets:
                sample_path = os.path.join(tmpdir, f"sample_{offset}.wav")

                ok = await extract_sample(
                    input_path=file_path,
                    output_path=sample_path,
                    offset=offset,
                    duration=duration,
                )
                if not ok:
                    # пропускаем — например, файл короче offset
                    continue

                result = await _recognize_sample(sample_path)
                if result and isinstance(result, dict):
                    track = result.get("track")
                    if track:
                        logger.info(
                            "Shazam matched at offset=%ds: %s — %s",
                            offset,
                            track.get("title"),
                            track.get("subtitle"),
                        )
                        return track

            return None


# === Парсинг ответа Shazam ===

def parse_track(track: dict) -> dict:
    """
    Извлекает удобные поля из ответа Shazam-track.

    Возвращает dict с ключами:
        title, artist, album, year, genre, cover_url, shazam_id,
        links: {youtube, spotify, apple_music}
    """
    title = track.get("title") or "Unknown"
    artist = track.get("subtitle") or "Unknown"
    shazam_id = track.get("key")

    # обложка
    cover_url = None
    images = track.get("images") or {}
    if isinstance(images, dict):
        cover_url = (
            images.get("coverarthq")
            or images.get("coverart")
            or images.get("background")
        )

    # альбом, год, жанр — лежат в sections[type=SONG].metadata
    album = None
    year = None
    sections = track.get("sections") or []
    for section in sections:
        if not isinstance(section, dict):
            continue
        if section.get("type") == "SONG":
            for meta in section.get("metadata") or []:
                if not isinstance(meta, dict):
                    continue
                title_meta = (meta.get("title") or "").lower()
                text = meta.get("text")
                if title_meta == "album" and text:
                    album = text
                elif title_meta == "released" and text:
                    year = text

    # жанр
    genre = None
    genres = track.get("genres") or {}
    if isinstance(genres, dict):
        genre = genres.get("primary")

    # ссылки на стриминги
    links: dict[str, str | None] = {
        "youtube": None,
        "spotify": None,
        "apple_music": None,
    }

    # apple music: hub.actions[type=uri].uri или hub.options
    hub = track.get("hub") or {}
    if isinstance(hub, dict):
        for action in hub.get("actions") or []:
            if not isinstance(action, dict):
                continue
            uri = action.get("uri") or ""
            if action.get("type") == "applemusicplay" or "music.apple.com" in uri:
                if uri.startswith("http"):
                    links["apple_music"] = uri

    # youtube + spotify: ищем в sections[type=RELATED]/providers и в hub.providers
    for section in sections:
        if not isinstance(section, dict):
            continue
        # provider-блоки
        providers = section.get("providers") or []
        for p in providers:
            if not isinstance(p, dict):
                continue
            ptype = (p.get("type") or "").lower()
            actions = p.get("actions") or []
            uri = None
            for a in actions:
                if isinstance(a, dict):
                    uri = a.get("uri") or a.get("url")
                    if uri:
                        break
            if not uri:
                continue
            if "spotify" in ptype or "spotify.com" in uri:
                links["spotify"] = uri
            elif "youtube" in ptype or "youtube.com" in uri or "youtu.be" in uri:
                links["youtube"] = uri

        # type=VIDEO с youtube
        if section.get("type") == "VIDEO":
            yt = section.get("youtubeurl")
            if isinstance(yt, dict):
                actions = yt.get("actions") or []
                for a in actions:
                    if isinstance(a, dict) and a.get("uri"):
                        links["youtube"] = links["youtube"] or a["uri"]

    return {
        "title": title,
        "artist": artist,
        "album": album,
        "year": year,
        "genre": genre,
        "cover_url": cover_url,
        "shazam_id": shazam_id,
        "links": links,
    }
