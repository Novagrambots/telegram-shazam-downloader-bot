"""Точка входа — запуск Shazam-бота"""
import asyncio
import logging
import os
import sys
import time

# uvloop ускоряет asyncio в 2-4 раза (не работает на Windows!)
try:
    import uvloop
    uvloop.install()
except ImportError:
    pass  # на Windows — работаем без uvloop

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from bot.config import settings

# настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# флаг-файл для crash recovery
CRASH_FLAG = ".crash_flag"


async def main() -> None:
    """Инициализация и запуск бота"""
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем хэндлеры (порядок важен!)
    from bot.handlers import start, admin, shazam
    dp.include_router(start.router)
    dp.include_router(admin.router)
    dp.include_router(shazam.router)  # TODO: последний — ловит медиасообщения

    # подключаем мидлвари
    from bot.middlewares.rate_limit import RateLimitMiddleware
    from bot.middlewares.subscription import SubscriptionMiddleware

    dp.message.middleware(RateLimitMiddleware())
    dp.message.middleware(SubscriptionMiddleware())
    dp.callback_query.middleware(SubscriptionMiddleware())

    # фоновая очистка памяти и временных файлов
    async def _background_cleanup() -> None:
        """Фоновая задача: очистка памяти и /tmp каждые 5 минут"""
        import glob
        from bot.middlewares.rate_limit import cleanup_stale_entries
        while True:
            await asyncio.sleep(300)  # 5 минут
            # чистим протухшие записи rate limit (memory leak)
            removed = cleanup_stale_entries()
            if removed:
                logger.info("Фоновая очистка: удалено %d записей rate limit", removed)
            # чистим старые файлы /tmp/shazam_bot (старше 30 минут)
            now = time.time()
            cutoff = now - 30 * 60
            cleaned = 0
            for f in glob.glob("/tmp/shazam_bot/**/*", recursive=True):
                try:
                    if os.path.isfile(f) and os.path.getmtime(f) < cutoff:
                        os.remove(f)
                        cleaned += 1
                except OSError:
                    pass
            if cleaned:
                logger.info("Фоновая очистка: удалено %d временных файлов из /tmp/shazam_bot", cleaned)

    @dp.startup()
    async def on_startup() -> None:
        # создаём таблицы в БД
        from bot.database import engine
        from bot.database.models import Base
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Таблицы БД созданы")

        # проверяем crash recovery
        if os.path.exists(CRASH_FLAG):
            logger.warning("Обнаружен crash-flag — предыдущий запуск завершился аварийно")
            os.remove(CRASH_FLAG)

        # ставим crash-flag (уберём при нормальном завершении)
        with open(CRASH_FLAG, "w") as f:
            f.write("running")

        # создаём временную директорию
        os.makedirs("/tmp/shazam_bot", exist_ok=True)

        # запускаем фоновую очистку
        asyncio.create_task(_background_cleanup())
        logger.info("Фоновая очистка запущена (интервал 5 мин)")

        bot_info = await bot.get_me()
        # автозаполнение bot_username, если в .env не задано — для рекламной подписи
        if not settings.bot_username and bot_info.username:
            settings.bot_username = bot_info.username
        logger.info(f"Бот @{bot_info.username} запущен!")

        # ставим дефолтное меню команд (глобально, ru — для новых юзеров)
        from bot.utils.commands import set_default_commands
        await set_default_commands(bot)
        logger.info("Дефолтное меню команд установлено")

    @dp.shutdown()
    async def on_shutdown() -> None:
        # убираем crash-flag при нормальном завершении
        if os.path.exists(CRASH_FLAG):
            os.remove(CRASH_FLAG)
        logger.info("Бот остановлен")

    # запускаем polling
    try:
        logger.info("Запуск polling...")
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
