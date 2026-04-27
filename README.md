# bot_4_shazam — Telegram-бот для распознавания музыки

Бот принимает аудио, голосовые сообщения и видео, нарезает сэмпл через ffmpeg
и распознаёт трек через Shazam API.

## Стек

- Python 3.12
- aiogram 3.x
- SQLAlchemy + asyncpg (PostgreSQL)
- shazamio
- ffmpeg

## Быстрый старт

```bash
cp .env.example .env
# заполнить BOT_TOKEN, ADMIN_IDS в .env

docker compose up -d
```

## Структура

```
bot/
├── main.py              # точка входа
├── config.py            # настройки из .env
├── i18n.py              # переводы ru/uz/en
├── emojis.py            # кастомные эмодзи
├── database/            # модели и CRUD
├── handlers/            # start, admin, shazam (TODO)
├── middlewares/         # subscription, rate_limit
├── keyboards/           # inline, admin
├── services/            # shazam (TODO)
└── utils/               # команды меню
```

