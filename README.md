# Telegram-бот для распознавания и скачивания музыки

Бот принимает голосовое, аудио или видео, распознаёт трек через Shazam,
скачивает аудиофайл с YouTube (yt-dlp) и присылает его пользователю —
с обложкой, исполнителем и названием.

## Возможности

- Распознавание трека из voice / audio / video / video_note / документа (audio/video MIME)
- Адаптивный подбор семплов (5/30/60 сек) с учётом длительности файла
- Скачивание аудио в нативном m4a (без перекодирования) через yt-dlp
- Скачивание идёт через цепочку прокси: residential SOCKS5 → Cloudflare WARP → direct
- Если прямой YouTube-URL от Shazam не сработал — пробуем поиск `ytsearch1:{artist} - {title}`
- Обложка ресайзится в JPEG (1280×1280 для фото, 320×320 для thumbnail аудио)
- Мультиязычность: русский / узбекский / английский
- Подсказка пользователю, если запись короче 10 сек
- Админка: `/admin`, статистика распознаваний, топ-10 треков, рассылка, обязательная подписка на каналы

## Стек

- Python 3.12
- aiogram 3.x
- SQLAlchemy + asyncpg (PostgreSQL)
- shazamio
- yt-dlp
- Pillow
- ffmpeg / ffprobe

## Быстрый старт

```bash
cp .env.example .env
# заполнить BOT_TOKEN, ADMIN_IDS, DB_PASSWORD, PROXY_URL

docker compose up -d
```

## Прокси

Скачивание треков с YouTube идёт по цепочке:

1. Резидентный SOCKS5 (`PROXY_URL`)
2. Cloudflare WARP (контейнер `warp`)
3. Direct

Если первый вариант упал — пробуем следующий. WARP поднимается вместе с остальными сервисами автоматически и не требует ключей.

### Использовать резидентный SOCKS5

В `.env`:
```
PROXY_URL=socks5://user:pass@host:port
```

## Структура

```
bot/
├── main.py                          # точка входа, polling, фоновая очистка
├── config.py                        # настройки из .env
├── i18n.py                          # переводы ru/uz/en
├── emojis.py                        # кастомные эмодзи
├── database/                        # модели User / Channel / ShazamRequest, CRUD
├── handlers/
│   ├── start.py                     # /start, /help, /profile, /lang
│   ├── admin.py                     # /admin, статистика, каналы, рассылка
│   └── shazam.py                    # приём медиа, распознавание, отправка трека
├── services/
│   ├── shazam.py                    # ffprobe + ffmpeg + shazamio
│   └── track_downloader.py          # yt-dlp с fallback-цепочкой прокси
├── middlewares/                     # subscription, rate_limit
├── keyboards/                       # inline, admin
└── utils/                           # меню команд
```

## Переменные окружения

| Переменная        | Описание                                              | Дефолт                  |
|-------------------|-------------------------------------------------------|-------------------------|
| `BOT_TOKEN`       | Токен от @BotFather                                   | —                       |
| `ADMIN_IDS`       | ID админов через запятую                              | пусто                   |
| `ADMIN_USERNAME`  | Юзернейм для контакта в /help                         | `admin`                 |
| `DB_HOST`         | Хост PostgreSQL                                       | `localhost`             |
| `DB_PORT`         | Порт                                                  | `5432`                  |
| `DB_NAME`         | Имя БД                                                | `bot_4_shazam`          |
| `DB_USER`         | Пользователь                                          | `postgres`              |
| `DB_PASSWORD`     | Пароль                                                | пусто                   |
| `PROXY_URL`       | Резидентный SOCKS5 для yt-dlp (`socks5://user:pass@host:port`) | —              |
| `MAX_INPUT_MB`    | Лимит размера входящего файла, МБ                     | `20`                    |
| `SAMPLE_DURATION` | Длина семпла для Shazam, сек                          | `15`                    |
