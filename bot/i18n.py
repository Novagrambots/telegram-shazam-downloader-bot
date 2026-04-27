"""Мультиязычность — русский, узбекский, английский
Использование: from bot.i18n import t
  t("start.welcome", lang="en", name="John")
"""

from bot.emojis import E

TRANSLATIONS = {
    # === /start ===
    "start.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет, {{name}}!</b>\n\n"
            f"{E['music']} Узнаю трек из аудио или видео и пришлю тебе саму песню.\n\n"
            f"{E['pin']} <b>Как пользоваться:</b>\n"
            "Отправь мне голосовое, аудио или видео — определю исполнителя, "
            f"название и скачаю аудиофайл. {E['plane']}\n\n"
            "Выбери действие ниже:"
        ),
        "uz": (
            f"{E['bot']} <b>Salom, {{name}}!</b>\n\n"
            f"{E['music']} Audio yoki videodan trekni aniqlayman va qo'shiqning o'zini yuboraman.\n\n"
            f"{E['pin']} <b>Qanday foydalanish:</b>\n"
            "Menga ovozli xabar, audio yoki video yuboring — ijrochi va nomini aniqlab, "
            f"audio faylni yuklab beraman. {E['plane']}\n\n"
            "Quyidagi tugmalardan birini tanlang:"
        ),
        "en": (
            f"{E['bot']} <b>Hello, {{name}}!</b>\n\n"
            f"{E['music']} I'll identify a track from audio or video and send you the song itself.\n\n"
            f"{E['pin']} <b>How to use:</b>\n"
            "Send me a voice message, audio or video — I'll find the artist, title, "
            f"and download the audio file for you. {E['plane']}\n\n"
            "Choose an action below:"
        ),
    },

    # === Кнопки главного меню ===
    "btn.recognize": {
        "ru": "Найти и скачать трек",
        "uz": "Trekni topish va yuklab olish",
        "en": "Find & download track",
    },
    "btn.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "btn.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "btn.back": {
        "ru": "Назад",
        "uz": "Orqaga",
        "en": "Back",
    },
    "btn.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },

    # === Профиль ===
    "profile.title": {
        "ru": (
            f"{E['profile']} <b>Твой профиль</b>\n\n"
            f"{E['edit']} Имя: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['music']} Распознаваний (всего): {{downloads}}\n"
        ),
        "uz": (
            f"{E['profile']} <b>Sizning profilingiz</b>\n\n"
            f"{E['edit']} Ism: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['music']} Aniqlanganlar (jami): {{downloads}}\n"
        ),
        "en": (
            f"{E['profile']} <b>Your profile</b>\n\n"
            f"{E['edit']} Name: {{full_name}}\n"
            f"{E['info']} ID: <code>{{user_id}}</code>\n"
            f"{E['music']} Recognitions (total): {{downloads}}\n"
        ),
    },

    # === Помощь ===
    "help.text": {
        "ru": (
            f"{E['book']} <b>Помощь</b>\n\n"
            f"{E['star']} Отправь голосовое, аудио или видео\n"
            f"{E['star']} Бот определит исполнителя и название трека\n"
            f"{E['star']} Затем скачает и пришлёт тебе сам аудиофайл\n"
            f"{E['star']} Поддерживаются форматы: mp3, ogg, m4a, mp4, avi и другие\n"
            f"{E['lock']} Максимальный размер входящего файла: {{max_mb}} МБ\n\n"
            f"{E['plane']} По вопросам: @{{admin_username}}"
        ),
        "uz": (
            f"{E['book']} <b>Yordam</b>\n\n"
            f"{E['star']} Ovozli xabar, audio yoki video yuboring\n"
            f"{E['star']} Bot ijrochi va trek nomini aniqlaydi\n"
            f"{E['star']} So'ng audio faylni yuklab, sizga yuboradi\n"
            f"{E['star']} Qo'llab-quvvatlanadi: mp3, ogg, m4a, mp4, avi va boshqalar\n"
            f"{E['lock']} Maksimal kiruvchi fayl hajmi: {{max_mb}} MB\n\n"
            f"{E['plane']} Savollar uchun: @{{admin_username}}"
        ),
        "en": (
            f"{E['book']} <b>Help</b>\n\n"
            f"{E['star']} Send a voice message, audio or video\n"
            f"{E['star']} The bot will identify the artist and track name\n"
            f"{E['star']} Then it will download and send you the audio file\n"
            f"{E['star']} Supported formats: mp3, ogg, m4a, mp4, avi and more\n"
            f"{E['lock']} Maximum input file size: {{max_mb}} MB\n\n"
            f"{E['plane']} Contact: @{{admin_username}}"
        ),
    },

    # === Shazam: распознавание ===
    "shazam.send_media_prompt": {
        "ru": (
            f"{E['music']} <b>Привет!</b>\n\n"
            "Пришли мне голосовое, аудио или видео — узнаю трек и пришлю саму песню."
        ),
        "uz": (
            f"{E['music']} <b>Salom!</b>\n\n"
            "Menga ovozli xabar, audio yoki video yuboring — qo'shiqni aniqlab, "
            "audio faylini ham yuboraman."
        ),
        "en": (
            f"{E['music']} <b>Hey!</b>\n\n"
            "Send me a voice message, audio or video — I'll identify the track "
            "and send you the audio file."
        ),
    },
    "shazam.listening": {
        "ru": f"{E['search']} <b>Слушаю...</b>",
        "uz": f"{E['search']} <b>Tinglamoqda...</b>",
        "en": f"{E['search']} <b>Listening...</b>",
    },
    "shazam.searching": {
        "ru": f"{E['search']} <b>Ищу в базе Shazam...</b>",
        "uz": f"{E['search']} <b>Shazam bazasida qidirilmoqda...</b>",
        "en": f"{E['search']} <b>Searching Shazam database...</b>",
    },
    "shazam.not_recognized": {
        "ru": (
            f"{E['cross']} <b>Не смог распознать трек.</b>\n\n"
            "Попробуй другой фрагмент — желательно припев или вокал без шумов."
        ),
        "uz": (
            f"{E['cross']} <b>Qo'shiqni aniqlab bo'lmadi.</b>\n\n"
            "Boshqa fragment yuboring — lo'nda qo'shiq yoki shovqinsiz vokal yaxshiroq."
        ),
        "en": (
            f"{E['cross']} <b>Couldn't recognize the track.</b>\n\n"
            "Try a different fragment — preferably the chorus or clean vocals without noise."
        ),
    },
    "shazam.too_short": {
        "ru": (
            f"{E['cross']} <b>Не смог распознать трек.</b>\n\n"
            f"{E['clock']} Запись слишком короткая — попробуй записать подольше "
            "(хотя бы 10–15 секунд) и желательно припев или вокал без шумов."
        ),
        "uz": (
            f"{E['cross']} <b>Qo'shiqni aniqlab bo'lmadi.</b>\n\n"
            f"{E['clock']} Yozuv juda qisqa — uzunroq yozib ko'ring "
            "(kamida 10–15 soniya), eng yaxshisi shovqinsiz vokal yoki naqorat."
        ),
        "en": (
            f"{E['cross']} <b>Couldn't recognize the track.</b>\n\n"
            f"{E['clock']} The recording is too short — try recording a longer fragment "
            "(at least 10–15 seconds), preferably the chorus or clean vocals."
        ),
    },
    "shazam.downloading": {
        "ru": f"{E['download']} <b>Скачиваю аудио...</b>",
        "uz": f"{E['download']} <b>Audio yuklanmoqda...</b>",
        "en": f"{E['download']} <b>Downloading audio...</b>",
    },
    "shazam.download_failed": {
        "ru": (
            f"{E['warning']} <b>Не удалось скачать аудио.</b>\n\n"
            "Возможно, трек недоступен на YouTube или заблокирован в твоём регионе. "
            "Информация о треке выше — попробуй найти его по ссылкам на стриминги."
        ),
        "uz": (
            f"{E['warning']} <b>Audioni yuklab bo'lmadi.</b>\n\n"
            "Trek YouTube'da yo'q yoki sizning hududingizda bloklangan bo'lishi mumkin. "
            "Yuqorida trek haqida ma'lumot bor — striming xizmatlari havolalaridan foydalaning."
        ),
        "en": (
            f"{E['warning']} <b>Couldn't download the audio.</b>\n\n"
            "The track may be unavailable on YouTube or blocked in your region. "
            "Track info is shown above — try the streaming links."
        ),
    },
    "shazam.promo": {
        "ru": f"\n\n{E['music']} Распознавай музыку через @{{bot_username}}",
        "uz": f"\n\n{E['music']} @{{bot_username}} orqali musiqani aniqlang",
        "en": f"\n\n{E['music']} Recognize music via @{{bot_username}}",
    },
    "shazam.no_audio": {
        "ru": f"{E['warning']} <b>В файле нет звука.</b>\n\nПришли аудио или видео со звуком.",
        "uz": f"{E['warning']} <b>Faylda ovoz yo'q.</b>\n\nOvozli audio yoki video yuboring.",
        "en": f"{E['warning']} <b>No audio found in the file.</b>\n\nPlease send audio or video with sound.",
    },
    "shazam.service_unavailable": {
        "ru": (
            f"{E['warning']} <b>Сервис Shazam временно недоступен.</b>\n\n"
            "Попробуй ещё раз через минуту."
        ),
        "uz": (
            f"{E['warning']} <b>Shazam xizmati vaqtincha ishlamayapti.</b>\n\n"
            "Bir daqiqadan keyin qayta urinib ko'ring."
        ),
        "en": (
            f"{E['warning']} <b>Shazam service is temporarily unavailable.</b>\n\n"
            "Please try again in a minute."
        ),
    },
    "shazam.file_too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой.</b>\n\nМаксимальный размер: {{limit}} МБ.",
        "uz": f"{E['package']} <b>Fayl juda katta.</b>\n\nMaksimal hajm: {{limit}} MB.",
        "en": f"{E['package']} <b>File is too large.</b>\n\nMaximum size: {{limit}} MB.",
    },
    "shazam.result_caption": {
        "ru": (
            f"{E['music']} <b>{{title}}</b>\n"
            f"{E['profile']} {{artist}}\n"
            f"{E['folder']} Альбом: {{album}}\n"
            f"{E['clock']} Год: {{year}}\n"
            f"{E['star']} Жанр: {{genre}}"
        ),
        "uz": (
            f"{E['music']} <b>{{title}}</b>\n"
            f"{E['profile']} {{artist}}\n"
            f"{E['folder']} Albom: {{album}}\n"
            f"{E['clock']} Yil: {{year}}\n"
            f"{E['star']} Janr: {{genre}}"
        ),
        "en": (
            f"{E['music']} <b>{{title}}</b>\n"
            f"{E['profile']} {{artist}}\n"
            f"{E['folder']} Album: {{album}}\n"
            f"{E['clock']} Year: {{year}}\n"
            f"{E['star']} Genre: {{genre}}"
        ),
    },
    "shazam.btn_youtube": {
        "ru": "YouTube",
        "uz": "YouTube",
        "en": "YouTube",
    },
    "shazam.btn_spotify": {
        "ru": "Spotify",
        "uz": "Spotify",
        "en": "Spotify",
    },
    "shazam.btn_apple_music": {
        "ru": "Apple Music",
        "uz": "Apple Music",
        "en": "Apple Music",
    },

    # === Расширенная статистика админки ===
    "admin.stats_title": {
        "ru": f"{E['chart']} <b>Статистика распознаваний</b>",
        "uz": f"{E['chart']} <b>Aniqlanganlar statistikasi</b>",
        "en": f"{E['chart']} <b>Recognition statistics</b>",
    },
    "admin.stats_total": {
        "ru": "Всего: <b>{count}</b>",
        "uz": "Jami: <b>{count}</b>",
        "en": "Total: <b>{count}</b>",
    },
    "admin.stats_recognized": {
        "ru": "Распознано: <b>{count}</b>",
        "uz": "Aniqlandi: <b>{count}</b>",
        "en": "Recognized: <b>{count}</b>",
    },
    "admin.stats_failed": {
        "ru": "Не распознано: <b>{count}</b>",
        "uz": "Aniqlanmadi: <b>{count}</b>",
        "en": "Not recognized: <b>{count}</b>",
    },
    "admin.stats_top": {
        "ru": f"\n{E['star']} <b>Топ-10 треков:</b>",
        "uz": f"\n{E['star']} <b>Top-10 trekning:</b>",
        "en": f"\n{E['star']} <b>Top-10 tracks:</b>",
    },

    # === Подписка ===
    "sub.welcome": {
        "ru": (
            f"{E['bot']} <b>Привет!</b>\n\n"
            f"{E['music']} Этот бот распознаёт музыку из аудио и видео "
            "и присылает сам трек — быстро и бесплатно!\n\n"
            f"{E['lock']} <b>Для начала подпишись на каналы ниже:</b>\n\n"
            f"После подписки нажми «{E['check']} Проверить подписку»"
        ),
        "uz": (
            f"{E['bot']} <b>Salom!</b>\n\n"
            f"{E['music']} Bu bot audio va videodan musiqani aniqlab, "
            "trekning o'zini yuboradi — tez va bepul!\n\n"
            f"{E['lock']} <b>Boshlash uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
            f"Obuna bo'lgandan keyin «{E['check']} Obunani tekshirish» tugmasini bosing"
        ),
        "en": (
            f"{E['bot']} <b>Hello!</b>\n\n"
            f"{E['music']} This bot recognizes music from audio and video "
            "and sends you the track itself — fast and free!\n\n"
            f"{E['lock']} <b>To start, subscribe to the channels below:</b>\n\n"
            f"After subscribing, tap «{E['check']} Check subscription»"
        ),
    },
    "sub.not_subscribed": {
        "ru": (
            f"{E['cross']} <b>Ты ещё не подписался на все каналы:</b>\n\n"
            f"Подпишись и нажми «{E['check']} Проверить подписку» ещё раз."
        ),
        "uz": (
            f"{E['cross']} <b>Siz hali barcha kanallarga obuna bo'lmadingiz:</b>\n\n"
            f"Obuna bo'ling va «{E['check']} Obunani tekshirish» tugmasini qayta bosing."
        ),
        "en": (
            f"{E['cross']} <b>You haven't subscribed to all channels yet:</b>\n\n"
            f"Subscribe and tap «{E['check']} Check subscription» again."
        ),
    },
    "sub.success": {
        "ru": (
            f"{E['check']} <b>Отлично, {{name}}!</b>\n\n"
            f"Теперь ты можешь пользоваться ботом! {E['plane']}\n\n"
            "Отправь аудио или видео — узнаю трек и пришлю саму песню."
        ),
        "uz": (
            f"{E['check']} <b>Ajoyib, {{name}}!</b>\n\n"
            f"Endi siz botdan foydalanishingiz mumkin! {E['plane']}\n\n"
            "Audio yoki video yuboring — trekni aniqlab, qo'shiqning o'zini yuboraman."
        ),
        "en": (
            f"{E['check']} <b>Great, {{name}}!</b>\n\n"
            f"You can now use the bot! {E['plane']}\n\n"
            "Send audio or video — I'll identify the track and send you the song."
        ),
    },
    "btn.check_sub": {
        "ru": "Проверить подписку",
        "uz": "Obunani tekshirish",
        "en": "Check subscription",
    },
    "sub.check_alert_fail": {
        "ru": f"{E['cross']} Подпишись на все каналы!",
        "uz": f"{E['cross']} Barcha kanallarga obuna bo'ling!",
        "en": f"{E['cross']} Subscribe to all channels!",
    },
    "sub.check_alert_ok": {
        "ru": f"{E['check']} Подписка подтверждена!",
        "uz": f"{E['check']} Obuna tasdiqlandi!",
        "en": f"{E['check']} Subscription confirmed!",
    },
    "sub.not_required": {
        "ru": f"{E['check']} Подписка не требуется!",
        "uz": f"{E['check']} Obuna talab qilinmaydi!",
        "en": f"{E['check']} No subscription required!",
    },

    # === Ошибки ===
    "error.generic": {
        "ru": f"{E['cross']} <b>Что-то пошло не так</b>\n\nПопробуй позже.",
        "uz": f"{E['cross']} <b>Nimadir noto'g'ri ketdi</b>\n\nKeyinroq urinib ko'ring.",
        "en": f"{E['cross']} <b>Something went wrong</b>\n\nTry again later.",
    },
    "error.rate_limit": {
        "ru": f"{E['clock']} <b>Слишком много запросов!</b>\n\nПодожди {{seconds}} секунд и попробуй снова.",
        "uz": f"{E['clock']} <b>Juda ko'p so'rovlar!</b>\n\n{{seconds}} soniya kuting va qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Too many requests!</b>\n\nWait {{seconds}} seconds and try again.",
    },
    "error.file_too_large": {
        "ru": f"{E['package']} <b>Файл слишком большой</b>\n\nМаксимальный размер: {{max_mb}} МБ.",
        "uz": f"{E['package']} <b>Fayl juda katta</b>\n\nMaksimal hajm: {{max_mb}} MB.",
        "en": f"{E['package']} <b>File too large</b>\n\nMaximum size: {{max_mb}} MB.",
    },
    "error.timeout": {
        "ru": f"{E['clock']} <b>Превышено время ожидания</b>\n\nПопробуй ещё раз через пару минут.",
        "uz": f"{E['clock']} <b>Kutish vaqti tugadi</b>\n\nBir necha daqiqadan keyin qayta urinib ko'ring.",
        "en": f"{E['clock']} <b>Request timed out</b>\n\nPlease try again in a few minutes.",
    },

    # === Выбор языка ===
    "lang.choose": {
        "ru": f"{E['gear']} <b>Выберите язык:</b>",
        "uz": f"{E['gear']} <b>Tilni tanlang:</b>",
        "en": f"{E['gear']} <b>Choose language:</b>",
    },
    "lang.changed": {
        "ru": f"{E['check']} Язык изменён на русский",
        "uz": f"{E['check']} Til o'zbek tiliga o'zgartirildi",
        "en": f"{E['check']} Language changed to English",
    },

    # === Админ-панель ===
    "admin.title": {
        "ru": f"{E['gear']} <b>Админ-панель</b>\n\nВыбери действие:",
        "uz": f"{E['gear']} <b>Admin panel</b>\n\nAmalni tanlang:",
        "en": f"{E['gear']} <b>Admin panel</b>\n\nChoose an action:",
    },
    "admin.no_access": {
        "ru": f"{E['lock']} У тебя нет доступа к админке.",
        "uz": f"{E['lock']} Sizda admin panelga kirish huquqi yo'q.",
        "en": f"{E['lock']} You don't have access to admin panel.",
    },
    "admin.stats": {
        "ru": (
            f"{E['chart']} <b>Статистика бота</b>\n\n"
            f"{E['users']} Всего юзеров: <b>{{total_users}}</b>\n"
            f"{E['star']} Новых юзеров сегодня: <b>{{today_users}}</b>\n"
            f"{E['music']} Всего распознаваний: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Каналов: <b>{{total_channels}}</b>"
        ),
        "uz": (
            f"{E['chart']} <b>Bot statistikasi</b>\n\n"
            f"{E['users']} Jami foydalanuvchilar: <b>{{total_users}}</b>\n"
            f"{E['star']} Bugungi yangi foydalanuvchilar: <b>{{today_users}}</b>\n"
            f"{E['music']} Jami aniqlanganlar: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Kanallar: <b>{{total_channels}}</b>"
        ),
        "en": (
            f"{E['chart']} <b>Bot statistics</b>\n\n"
            f"{E['users']} Total users: <b>{{total_users}}</b>\n"
            f"{E['star']} New users today: <b>{{today_users}}</b>\n"
            f"{E['music']} Total recognitions: <b>{{total_downloads}}</b>\n"
            f"{E['megaphone']} Channels: <b>{{total_channels}}</b>"
        ),
    },
    "admin.channels_empty": {
        "ru": f"{E['megaphone']} <b>Каналы</b>\n\nСписок пуст. Добавь канал кнопкой ниже.",
        "uz": f"{E['megaphone']} <b>Kanallar</b>\n\nRo'yxat bo'sh. Quyidagi tugma orqali kanal qo'shing.",
        "en": f"{E['megaphone']} <b>Channels</b>\n\nList is empty. Add a channel using the button below.",
    },
    "admin.channels_title": {
        "ru": f"{E['megaphone']} <b>Каналы для подписки:</b>\n",
        "uz": f"{E['megaphone']} <b>Obuna kanallari:</b>\n",
        "en": f"{E['megaphone']} <b>Subscription channels:</b>\n",
    },
    "admin.add_channel_id": {
        "ru": (
            f"{E['megaphone']} <b>Добавление канала</b>\n\n"
            "Отправь <b>ID канала</b> (например <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Узнать ID: добавь бота @getmyid_bot в канал"
        ),
        "uz": (
            f"{E['megaphone']} <b>Kanal qo'shish</b>\n\n"
            "<b>Kanal ID</b> raqamini yuboring (masalan <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} ID bilish: @getmyid_bot ni kanalga qo'shing"
        ),
        "en": (
            f"{E['megaphone']} <b>Add channel</b>\n\n"
            "Send the <b>channel ID</b> (e.g. <code>-1001234567890</code>)\n\n"
            f"{E['bulb']} Get ID: add @getmyid_bot to the channel"
        ),
    },
    "admin.add_channel_title": {
        "ru": f"{E['edit']} Теперь отправь <b>название канала</b>:",
        "uz": f"{E['edit']} Endi <b>kanal nomini</b> yuboring:",
        "en": f"{E['edit']} Now send the <b>channel name</b>:",
    },
    "admin.add_channel_link": {
        "ru": (
            f"{E['link']} Теперь отправь <b>ссылку или юзернейм канала</b>\n\n"
            "Принимаю любой формат:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "uz": (
            f"{E['link']} Endi <b>kanal havolasi yoki username</b> yuboring\n\n"
            "Istalgan formatda:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
        "en": (
            f"{E['link']} Now send the <b>channel link or username</b>\n\n"
            "Any format accepted:\n"
            "• <code>https://t.me/your_channel</code>\n"
            "• <code>@your_channel</code>\n"
            "• <code>your_channel</code>"
        ),
    },
    "admin.channel_added": {
        "ru": f"{E['check']} <b>Канал добавлен!</b>",
        "uz": f"{E['check']} <b>Kanal qo'shildi!</b>",
        "en": f"{E['check']} <b>Channel added!</b>",
    },
    "admin.confirm_delete": {
        "ru": f"{E['warning']} <b>Удалить канал?</b>\n\nID: <code>{{channel_id}}</code>\n\nЭто действие нельзя отменить.",
        "uz": f"{E['warning']} <b>Kanalni o'chirishni xohlaysizmi?</b>\n\nID: <code>{{channel_id}}</code>\n\nBu amalni qaytarib bo'lmaydi.",
        "en": f"{E['warning']} <b>Delete channel?</b>\n\nID: <code>{{channel_id}}</code>\n\nThis action cannot be undone.",
    },
    "admin.id_not_number": {
        "ru": f"{E['cross']} ID должен быть числом. Попробуй ещё раз:",
        "uz": f"{E['cross']} ID raqam bo'lishi kerak. Qayta urinib ko'ring:",
        "en": f"{E['cross']} ID must be a number. Try again:",
    },
    "admin.title_too_long": {
        "ru": f"{E['cross']} Название слишком длинное (макс 200 символов)",
        "uz": f"{E['cross']} Nom juda uzun (maks 200 belgi)",
        "en": f"{E['cross']} Name is too long (max 200 characters)",
    },
    "admin.link_invalid": {
        "ru": f"{E['cross']} Не удалось распознать ссылку.\nПопробуй ещё:",
        "uz": f"{E['cross']} Havolani aniqlab bo'lmadi.\nQayta urinib ko'ring:",
        "en": f"{E['cross']} Could not parse the link.\nTry again:",
    },

    # === Кнопки админки ===
    "btn.admin_stats": {"ru": "Статистика", "uz": "Statistika", "en": "Statistics"},
    "btn.admin_channels": {"ru": "Каналы", "uz": "Kanallar", "en": "Channels"},
    "btn.admin_home": {"ru": "Главное меню", "uz": "Bosh menyu", "en": "Main menu"},
    "btn.admin_add": {"ru": "Добавить канал", "uz": "Kanal qo'shish", "en": "Add channel"},
    "btn.admin_back": {"ru": "Назад", "uz": "Orqaga", "en": "Back"},
    "btn.admin_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_confirm_del": {"ru": "Да, удалить", "uz": "Ha, o'chirish", "en": "Yes, delete"},
    "btn.admin_cancel_del": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "btn.admin_panel": {"ru": "Админ-панель", "uz": "Admin panel", "en": "Admin panel"},
    "btn.admin_broadcast": {"ru": "Рассылка", "uz": "Xabar yuborish", "en": "Broadcast"},

    # === Рассылка ===
    "admin.broadcast_prompt": {
        "ru": f"{E['plane']} <b>Массовая рассылка</b>\n\nОтправь текст/фото/видео для рассылки.\nПоддерживается HTML.",
        "uz": f"{E['plane']} <b>Ommaviy xabar</b>\n\nYuborish uchun matn/rasm/video yuboring.\nHTML qo'llab-quvvatlanadi.",
        "en": f"{E['plane']} <b>Mass broadcast</b>\n\nSend text/photo/video to broadcast.\nHTML supported.",
    },
    "admin.broadcast_preview": {
        "ru": f"{E['eye']} <b>Предпросмотр</b>\n\nОтправить это сообщение всем юзерам?",
        "uz": f"{E['eye']} <b>Oldindan ko'rish</b>\n\nBu xabarni barcha foydalanuvchilarga yuborishni xohlaysizmi?",
        "en": f"{E['eye']} <b>Preview</b>\n\nSend this message to all users?",
    },
    "admin.broadcast_confirm": {"ru": "Да, отправить", "uz": "Ha, yuborish", "en": "Yes, send"},
    "admin.broadcast_cancel": {"ru": "Отмена", "uz": "Bekor qilish", "en": "Cancel"},
    "admin.broadcast_started": {
        "ru": f"{E['plane']} Рассылка запущена... Ожидай отчёт.",
        "uz": f"{E['plane']} Xabar yuborilmoqda... Hisobotni kuting.",
        "en": f"{E['plane']} Broadcast started... Wait for report.",
    },
    "admin.broadcast_done": {
        "ru": f"{E['chart']} <b>Рассылка завершена!</b>\n\n{E['check']} Доставлено: <b>{{success}}</b>\n{E['cross']} Ошибок: <b>{{failed}}</b>\n{E['users']} Всего: <b>{{total}}</b>",
        "uz": f"{E['chart']} <b>Xabar yuborish tugadi!</b>\n\n{E['check']} Yetkazildi: <b>{{success}}</b>\n{E['cross']} Xatolar: <b>{{failed}}</b>\n{E['users']} Jami: <b>{{total}}</b>",
        "en": f"{E['chart']} <b>Broadcast complete!</b>\n\n{E['check']} Delivered: <b>{{success}}</b>\n{E['cross']} Failed: <b>{{failed}}</b>\n{E['users']} Total: <b>{{total}}</b>",
    },

    # === Описания команд бота (для меню Telegram) ===
    "cmd.start": {
        "ru": "Запустить бота",
        "uz": "Botni boshlash",
        "en": "Start the bot",
    },
    "cmd.menu": {
        "ru": "Главное меню",
        "uz": "Asosiy menyu",
        "en": "Main menu",
    },
    "cmd.profile": {
        "ru": "Мой профиль",
        "uz": "Mening profilim",
        "en": "My profile",
    },
    "cmd.help": {
        "ru": "Помощь",
        "uz": "Yordam",
        "en": "Help",
    },
    "cmd.language": {
        "ru": "Сменить язык",
        "uz": "Tilni o'zgartirish",
        "en": "Change language",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    """Получить перевод по ключу и языку"""
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(lang, translations.get("ru", f"[{key}]"))
    if kwargs:
        text = text.format(**kwargs)
    return text


def detect_language(language_code: str | None) -> str:
    """Определяет язык по Telegram: ru → русский, uz → узбекский, остальное → английский"""
    if not language_code:
        return "en"
    if language_code.startswith("ru"):
        return "ru"
    if language_code.startswith("uz"):
        return "uz"
    return "en"
