"""Хэндлер распознавания музыки через Shazam.

Принимает медиафайл (voice/audio/video/video_note/document с audio|video mime),
скачивает во временную директорию, отдаёт в services/shazam.py и возвращает
результат: обложка + caption + кнопки YouTube/Spotify/Apple Music.

Все промежуточные файлы удаляются автоматически (TemporaryDirectory).
"""
from __future__ import annotations

import asyncio
import logging
import os
import tempfile
from io import BytesIO

import aiohttp
from PIL import Image

from aiogram import F, Router
from aiogram.types import (
    BufferedInputFile,
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from bot.config import settings
from bot.database import async_session
from bot.database.crud import (
    get_or_create_user,
    get_user_language,
    log_shazam_request,
)
from bot.emojis import E
from bot.i18n import t
from bot.services.shazam import (
    NoAudioError,
    ShazamServiceError,
    parse_track,
    recognize_audio,
)
from bot.services.track_downloader import (
    TrackDownloadError,
    download_track,
)

logger = logging.getLogger(__name__)
router = Router()


# === Утилиты ===

# Telegram требует thumbnail для audio: JPEG, ≤200 КБ, ≤320×320.
# Cover для send_photo: оставляем оригинальное разрешение, но конвертим в JPEG для надёжности.

async def _fetch_image(url: str, timeout: int = 10) -> bytes | None:
    """Скачивает картинку по URL. None при любой ошибке."""
    try:
        async with aiohttp.ClientSession() as sess:
            async with sess.get(url, timeout=aiohttp.ClientTimeout(total=timeout)) as resp:
                if resp.status != 200:
                    return None
                return await resp.read()
    except Exception as exc:
        logger.warning("Не удалось скачать картинку %s: %s", url, exc)
        return None


def _resize_to_jpeg(data: bytes, max_side: int, quality: int = 85) -> bytes | None:
    """Ресайзит картинку до квадрата max_side×max_side, конвертит в RGB JPEG."""
    try:
        img = Image.open(BytesIO(data))
        if img.mode != "RGB":
            img = img.convert("RGB")
        img.thumbnail((max_side, max_side), Image.LANCZOS)
        out = BytesIO()
        img.save(out, format="JPEG", quality=quality, optimize=True)
        return out.getvalue()
    except Exception as exc:
        logger.warning("Pillow не смог обработать картинку: %s", exc)
        return None


async def _prepare_covers(cover_url: str | None) -> tuple[BufferedInputFile | None, BufferedInputFile | None]:
    """
    Готовит две версии обложки из одного URL:
      - photo: до 1280×1280 JPEG (для send_photo)
      - thumb: до 320×320 JPEG ≤200КБ (для send_audio.thumbnail — лимит Telegram)
    Возвращает (photo, thumb). Любой может быть None.
    """
    if not cover_url:
        return None, None

    raw = await _fetch_image(cover_url)
    if not raw:
        return None, None

    # photo: высокое качество для отдельного сообщения с обложкой
    photo_bytes = await asyncio.to_thread(_resize_to_jpeg, raw, 1280, 90)
    photo = BufferedInputFile(photo_bytes, filename="cover.jpg") if photo_bytes else None

    # thumb: жёсткий лимит Telegram — 200КБ, 320×320
    thumb_bytes = await asyncio.to_thread(_resize_to_jpeg, raw, 320, 85)
    if thumb_bytes and len(thumb_bytes) > 200 * 1024:
        # ужимаем сильнее, если не влезли в лимит
        thumb_bytes = await asyncio.to_thread(_resize_to_jpeg, raw, 320, 70)
    thumb = BufferedInputFile(thumb_bytes, filename="thumb.jpg") if thumb_bytes else None

    return photo, thumb


def _detect_input(message: Message) -> tuple[str, str, int, int | None, str] | None:
    """
    Определяет параметры входящего медиа.

    Возвращает: (input_type, file_id, file_size, duration, ext) или None.
    """
    if message.voice:
        v = message.voice
        return "voice", v.file_id, v.file_size or 0, v.duration, "ogg"
    if message.audio:
        a = message.audio
        ext = "mp3"
        if a.file_name and "." in a.file_name:
            ext = a.file_name.rsplit(".", 1)[-1].lower()
        return "audio", a.file_id, a.file_size or 0, a.duration, ext
    if message.video:
        v = message.video
        return "video", v.file_id, v.file_size or 0, v.duration, "mp4"
    if message.video_note:
        vn = message.video_note
        return "video_note", vn.file_id, vn.file_size or 0, vn.duration, "mp4"
    if message.document:
        d = message.document
        mime = (d.mime_type or "").lower()
        if mime.startswith("audio/") or mime.startswith("video/"):
            ext = "bin"
            if d.file_name and "." in d.file_name:
                ext = d.file_name.rsplit(".", 1)[-1].lower()
            kind = "audio" if mime.startswith("audio/") else "video"
            return kind, d.file_id, d.file_size or 0, None, ext
    return None


def _build_links_keyboard(links: dict, lang: str) -> InlineKeyboardMarkup | None:
    """Собирает клавиатуру со ссылками на стриминги (только если url есть)."""
    row = []
    if links.get("youtube"):
        row.append(InlineKeyboardButton(
            text=t("shazam.btn_youtube", lang),
            url=links["youtube"],
        ))
    if links.get("spotify"):
        row.append(InlineKeyboardButton(
            text=t("shazam.btn_spotify", lang),
            url=links["spotify"],
        ))
    if links.get("apple_music"):
        row.append(InlineKeyboardButton(
            text=t("shazam.btn_apple_music", lang),
            url=links["apple_music"],
        ))
    if not row:
        return None
    # размещаем по 2 в ряд
    rows = [row[i:i + 2] for i in range(0, len(row), 2)]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# === Основной хэндлер ===

@router.message(
    F.voice | F.audio | F.video | F.video_note
    | (F.document & (
        F.document.mime_type.startswith("audio/")
        | F.document.mime_type.startswith("video/")
    ))
)
async def handle_media(message: Message) -> None:
    """Принимает медиа, распознаёт трек, отправляет результат."""
    info = _detect_input(message)
    if info is None:
        return

    input_type, file_id, file_size, duration, ext = info

    # язык юзера + регистрация — поднимаем ВЫШЕ try, чтобы внешний except мог использовать lang
    async with async_session() as session:
        await get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )
        lang = await get_user_language(session, message.from_user.id)

    # проверка размера
    limit_bytes = settings.max_input_mb * 1024 * 1024
    if file_size and file_size > limit_bytes:
        await message.answer(
            t("shazam.file_too_large", lang, limit=settings.max_input_mb),
            parse_mode="HTML",
        )
        return

    # статусное сообщение
    status_msg = await message.answer(
        t("shazam.listening", lang),
        parse_mode="HTML",
    )

    os.makedirs("/tmp/shazam_bot", exist_ok=True)

    # флаги для финального логирования (заполняются по ходу)
    recognized = False
    parsed: dict | None = None

    try:
        with tempfile.TemporaryDirectory(prefix="in_", dir="/tmp/shazam_bot") as tmpdir:
            input_path = os.path.join(tmpdir, f"input.{ext}")

            # скачиваем файл
            try:
                tg_file = await message.bot.get_file(file_id)
                await message.bot.download_file(tg_file.file_path, input_path)
            except Exception as exc:
                logger.exception("Ошибка скачивания файла: %s", exc)
                await status_msg.edit_text(
                    t("error.generic", lang),
                    parse_mode="HTML",
                )
                return

            # обновляем статус
            try:
                await status_msg.edit_text(
                    t("shazam.searching", lang),
                    parse_mode="HTML",
                )
            except Exception:
                pass  # не критично

            # распознавание
            try:
                track = await recognize_audio(
                    input_path,
                    duration=settings.sample_duration,
                )
            except NoAudioError:
                await status_msg.edit_text(
                    t("shazam.no_audio", lang),
                    parse_mode="HTML",
                )
                return
            except ShazamServiceError as exc:
                logger.warning("Shazam service error: %s", exc)
                await status_msg.edit_text(
                    t("shazam.service_unavailable", lang),
                    parse_mode="HTML",
                )
                return
            except Exception as exc:
                logger.exception("Ошибка распознавания: %s", exc)
                await status_msg.edit_text(
                    t("error.generic", lang),
                    parse_mode="HTML",
                )
                return

        # === Результат ===
        if track:
            parsed = parse_track(track)
            recognized = True
            caption = t(
                "shazam.result_caption",
                lang,
                title=parsed["title"],
                artist=parsed["artist"],
                album=parsed["album"] or "—",
                year=parsed["year"] or "—",
                genre=parsed["genre"] or "—",
            )
            # рекламная подпись
            if settings.bot_username:
                caption += t("shazam.promo", lang, bot_username=settings.bot_username)
            keyboard = _build_links_keyboard(parsed["links"], lang)
            cover_url = parsed.get("cover_url")

            # подготавливаем обложки (одно скачивание → две версии: для photo и для thumbnail)
            photo_file, thumb_file = await _prepare_covers(cover_url)

            # 1) сначала шлём фото/текст с метаданными
            sent_ok = False
            if photo_file:
                try:
                    await message.answer_photo(
                        photo=photo_file,
                        caption=caption,
                        reply_markup=keyboard,
                        parse_mode="HTML",
                    )
                    sent_ok = True
                except Exception as exc:
                    logger.warning("Не удалось отправить фото-результат: %s", exc)

            if not sent_ok:
                await message.answer(
                    caption,
                    reply_markup=keyboard,
                    parse_mode="HTML",
                )

            # 2) пытаемся скачать и отправить аудио
            try:
                await status_msg.edit_text(
                    t("shazam.downloading", lang),
                    parse_mode="HTML",
                )
            except Exception:
                pass

            try:
                with tempfile.TemporaryDirectory(prefix="dl_", dir="/tmp/shazam_bot") as dl_dir:
                    downloaded = await download_track(
                        youtube_url=parsed["links"].get("youtube"),
                        title=parsed["title"],
                        artist=parsed["artist"],
                        output_dir=dl_dir,
                    )
                    audio = FSInputFile(
                        downloaded.file_path,
                        filename=f"{parsed['artist']} - {parsed['title']}.{downloaded.ext}",
                    )
                    audio_caption = (
                        f"{E['music']} <b>{parsed['title']}</b> — {parsed['artist']}"
                    )
                    if settings.bot_username:
                        audio_caption += t(
                            "shazam.promo", lang, bot_username=settings.bot_username
                        )
                    await message.answer_audio(
                        audio=audio,
                        title=parsed["title"],
                        performer=parsed["artist"],
                        duration=downloaded.duration or None,
                        thumbnail=thumb_file,
                        caption=audio_caption,
                        parse_mode="HTML",
                    )
            except TrackDownloadError as exc:
                logger.warning("Не удалось скачать трек: %s", exc)
                try:
                    await message.answer(
                        t("shazam.download_failed", lang),
                        parse_mode="HTML",
                    )
                except Exception:
                    pass
            except Exception as exc:
                logger.exception("Непредвиденная ошибка при скачивании трека: %s", exc)

            # успех — удаляем статусное сообщение
            try:
                await status_msg.delete()
            except Exception:
                pass
        else:
            # не распознали — если запись слишком короткая, просим записать подольше
            if duration is not None and duration < 10:
                fail_key = "shazam.too_short"
            else:
                fail_key = "shazam.not_recognized"
            await status_msg.edit_text(
                t(fail_key, lang),
                parse_mode="HTML",
            )
    except Exception as exc:
        logger.exception("Непредвиденная ошибка в handle_media: %s", exc)
        try:
            await status_msg.edit_text(
                t("error.generic", lang),
                parse_mode="HTML",
            )
        except Exception:
            pass
    finally:
        # единая точка логирования в БД — в любом исходе
        try:
            async with async_session() as session:
                await log_shazam_request(
                    session=session,
                    user_id=message.from_user.id,
                    input_type=input_type,
                    input_duration=duration,
                    recognized=recognized,
                    track_title=parsed["title"] if recognized and parsed else None,
                    track_artist=parsed["artist"] if recognized and parsed else None,
                    shazam_track_id=parsed.get("shazam_id") if recognized and parsed else None,
                )
        except Exception as log_exc:
            logger.warning("Не удалось записать log_shazam_request: %s", log_exc)
