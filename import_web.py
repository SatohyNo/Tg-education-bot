#!/usr/bin/env python3
"""Імпорт історії групи, витягнутої з Telegram Web (tg_history_*.json), у messages.jsonl.

Формат: [{mid, topic, ts, author, text, files: [..], photo: bool}, ...].
Повідомлення бота та команди /dz пропускаються, повтори не дублюються.
Бот на час імпорту краще зупинити. Після імпорту файл переноситься в import/ поруч зі скриптом.
"""
import glob, json, os, re, shutil, sys

OUT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(OUT, "messages.jsonl")
IMPORT = os.path.join(OUT, "import")
CFG = json.load(open(os.path.join(OUT, "config.json"), encoding="utf-8"))
GROUP = CFG["group"]
BOT_NAME = CFG.get("bot_name", "")  # ім'я бота в чаті — його повідомлення не імпортуються
PUA = re.compile("[\ue000-\uf8ff]")  # іконки інтерфейсу Telegram Web


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.expanduser("~/Downloads/tg_history_*.json")), key=os.path.getmtime)[-1:]
    if not paths:
        sys.exit("Не знайшов ~/Downloads/tg_history_*.json")
    rows = [json.loads(line) for line in open(DB, encoding="utf-8")]
    gid = next((m["chat_id"] for m in rows if m.get("chat") == GROUP), None)
    if gid is None:
        sys.exit(f"У {DB} ще немає повідомлень групи {GROUP}, не знаю її chat_id.")
    existing = {(m["date"], m["text"]): m for m in rows}

    for path in paths:
        data = sorted(json.load(open(path, encoding="utf-8")), key=lambda m: m["ts"])
        last_author, added = {}, 0
        for m in data:
            topic = m.get("topic") or "General"
            # Telegram Web не підписує підряд ідучі повідомлення одного автора
            who = m.get("author") or last_author.get(topic) or "?"
            last_author[topic] = who
            text = PUA.sub("", m.get("text") or "").strip()
            files = ", ".join(m.get("files") or []) or ("фото" if m.get("photo") else "")
            if (BOT_NAME and who == BOT_NAME) or text.startswith("/dz") or (not text and not files):
                continue
            # час у вебі може відрізнятися від Bot API на секунду-дві
            old = next((existing[(m["ts"] + d, text)] for d in range(-3, 4) if (m["ts"] + d, text) in existing), None)
            if old:  # бот уже зберіг — лише додаємо тему
                old.setdefault("topic", topic)
                continue
            row = {"date": m["ts"], "chat_id": gid, "chat": GROUP, "topic": topic, "who": who,
                   "text": text, "file": files}
            existing[(m["ts"], text)] = row
            rows.append(row)
            added += 1
        os.makedirs(IMPORT, exist_ok=True)
        shutil.move(path, os.path.join(IMPORT, os.path.basename(path)))
        print(f"Імпортовано {added} з {len(data)} повідомлень ({os.path.basename(path)})")

    tmp = DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for m in sorted(rows, key=lambda m: m["date"]):
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    os.replace(tmp, DB)


main()
