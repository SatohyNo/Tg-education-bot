# hw_bot — бот домашніх завдань для Telegram-групи

Бот сидить у групі (форум, теми = предмети), зберігає всі повідомлення і через
[Claude Code](https://claude.com/claude-code) (`claude -p`) веде список ДЗ у `tasks.json`.
Чистий Python 3, без сторонніх бібліотек.

## Що вміє

- **Щосуботи о 18:00** надсилає в групу всі активні ДЗ, задані цього тижня з понеділка по суботу,
  незалежно від дедлайну (якщо Mac спав — надішле пізніше, але до 22:00).
- `/dz [N]` — що здавати в найближчі N днів (за замовчуванням 7, максимум 30).
- Повідомлення з ДЗ, переслані боту в особисті учасником групи, додаються до списку.
- Якщо Claude недоступний — `/dz` шукає ДЗ за ключовими словами.

## Встановлення

1. Створи бота в [@BotFather](https://t.me/BotFather), вимкни йому Privacy Mode
   (`/setprivacy` → Disable), додай у групу.
2. Збережи токен у файл (у коді його немає):
   ```sh
   echo "123456:ABC..." > ~/.hw_bot_token && chmod 600 ~/.hw_bot_token
   ```
3. Встанови й залогінь [Claude Code](https://claude.com/claude-code) (`~/.local/bin/claude`).
4. Створи `config.json` за зразком `config.example.json`:
   ```sh
   cp config.example.json config.json
   ```
   - `group` — назва групи (так само, як у Telegram);
   - `about` — коротко про групу для Claude (університет, курс), можна порожнє;
   - `bot_name` — ім'я бота в чаті, щоб `import_web.py` пропускав його повідомлення;
   - `subjects` — предмети; ДЗ розкладаються саме за ними.
5. Запуск:
   ```sh
   python3 -u hw_bot.py
   ```

### Автозапуск на macOS

Скопіюй `com.example.hwbot.plist` у `~/Library/LaunchAgents/`, заміни `/ABSOLUTE/PATH/TO`
на шлях до папки бота і виконай:
```sh
launchctl load ~/Library/LaunchAgents/com.example.hwbot.plist
```

## Налаштування (`hw_bot.py`)

| Константа | Значення |
|---|---|
| `WEEKLY_DAY, WEEKLY_FROM, WEEKLY_UNTIL` | день (5 = субота) і години суботньої розсилки |
| `DZ_DAYS`, `DZ_MAX` | горизонт `/dz` за замовчуванням і максимум |
| `UPDATE_EVERY` | як часто оновлювати список через Claude |
| `MSG_DAYS` | скільки днів історії чату враховувати |

## Імпорт історії

- `import_export.py` — з Telegram Desktop (Export chat history → JSON).
- `import_web.py` — з JSON, витягнутого з Telegram Web.

## Дані

Усе, що бот збирає (`messages.jsonl`, `tasks.json`, `files/`, логи), лежить поруч зі скриптом
разом із `config.json` і виключене з git через `.gitignore`.
