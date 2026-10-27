# hw_bot — homework bot for a Telegram group

The bot lives in a group (a forum where topics = subjects), stores every message and uses
[Claude Code](https://claude.com/claude-code) (`claude -p`) to maintain a homework list in `tasks.json`.
Pure Python 3, no third-party libraries.

## Features

- **Every Saturday at 18:00** it posts to the group all active homework assigned this week from Monday
  to Saturday, regardless of the deadline (if the Mac was asleep, it posts later, but before 22:00).
- `/dz [N]` — what is due in the next N days (7 by default, 30 at most).
- Homework messages forwarded to the bot in a private chat by a group member are added to the list.
- If Claude is unavailable, `/dz` falls back to a keyword search.

## Installation

1. Create a bot with [@BotFather](https://t.me/BotFather), turn off its Privacy Mode
   (`/setprivacy` → Disable) and add it to the group.
2. Save the token to a file (it is not in the code):
   ```sh
   echo "123456:ABC..." > ~/.hw_bot_token && chmod 600 ~/.hw_bot_token
   ```
3. Install and log in to [Claude Code](https://claude.com/claude-code) (`~/.local/bin/claude`).
4. Create `config.json` from `config.example.json`:
   ```sh
   cp config.example.json config.json
   ```
   - `group` — the group name (exactly as in Telegram);
   - `about` — a short note about the group for Claude (university, year), may be empty;
   - `bot_name` — the bot's display name in the chat, so `import_web.py` skips its messages;
   - `subjects` — the subjects; homework is sorted into exactly these.
5. Run:
   ```sh
   python3 -u hw_bot.py
   ```

### Autostart on macOS

Copy `com.example.hwbot.plist` to `~/Library/LaunchAgents/`, replace `/ABSOLUTE/PATH/TO`
with the path to the bot folder and run:
```sh
launchctl load ~/Library/LaunchAgents/com.example.hwbot.plist
```

## Settings (`hw_bot.py`)

| Constant | Meaning |
|---|---|
| `WEEKLY_DAY, WEEKLY_FROM, WEEKLY_UNTIL` | day (5 = Saturday) and hours of the Saturday digest |
| `DZ_DAYS`, `DZ_MAX` | default and maximum `/dz` horizon |
| `UPDATE_EVERY` | how often the list is refreshed through Claude |
| `MSG_DAYS` | how many days of chat history to consider |

## Importing history

- `import_export.py` — from Telegram Desktop (Export chat history → JSON).
- `import_web.py` — from JSON extracted from Telegram Web.

## Data

Everything the bot collects (`messages.jsonl`, `tasks.json`, `files/`, logs) is stored next to the script
together with `config.json` and is excluded from git via `.gitignore`.

Note: the bot's replies in Telegram and the prompt for Claude are in Ukrainian.
