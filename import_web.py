#!/usr/bin/env python3
"""Imports group history extracted from Telegram Web (tg_history_*.json) into messages.jsonl.

Format: [{mid, topic, ts, author, text, files: [..], photo: bool}, ...].
Bot messages and /dz commands are skipped, duplicates are not added.
Better stop the bot while importing. After import the file is moved to import/ next to the script.
"""
import glob, json, os, re, shutil, sys

OUT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(OUT, "messages.jsonl")
IMPORT = os.path.join(OUT, "import")
CFG = json.load(open(os.path.join(OUT, "config.json"), encoding="utf-8"))
GROUP = CFG["group"]
BOT_NAME = CFG.get("bot_name", "")  # the bot's name in the chat — its messages are not imported
PUA = re.compile("[\ue000-\uf8ff]")  # Telegram Web UI icons


def main():
    paths = sys.argv[1:] or sorted(glob.glob(os.path.expanduser("~/Downloads/tg_history_*.json")), key=os.path.getmtime)[-1:]
    if not paths:
        sys.exit("~/Downloads/tg_history_*.json not found")
    rows = [json.loads(line) for line in open(DB, encoding="utf-8")]
    gid = next((m["chat_id"] for m in rows if m.get("chat") == GROUP), None)
    if gid is None:
        sys.exit(f"{DB} has no messages from group {GROUP} yet, its chat_id is unknown.")
    existing = {(m["date"], m["text"]): m for m in rows}

    for path in paths:
        data = sorted(json.load(open(path, encoding="utf-8")), key=lambda m: m["ts"])
        last_author, added = {}, 0
        for m in data:
            topic = m.get("topic") or "General"
            # Telegram Web doesn't label consecutive messages from the same author
            who = m.get("author") or last_author.get(topic) or "?"
            last_author[topic] = who
            text = PUA.sub("", m.get("text") or "").strip()
            files = ", ".join(m.get("files") or []) or ("фото" if m.get("photo") else "")
            if (BOT_NAME and who == BOT_NAME) or text.startswith("/dz") or (not text and not files):
                continue
            # web timestamps may differ from the Bot API by a second or two
            old = next((existing[(m["ts"] + d, text)] for d in range(-3, 4) if (m["ts"] + d, text) in existing), None)
            if old:  # the bot already saved it — just add the topic
                old.setdefault("topic", topic)
                continue
            row = {"date": m["ts"], "chat_id": gid, "chat": GROUP, "topic": topic, "who": who,
                   "text": text, "file": files}
            existing[(m["ts"], text)] = row
            rows.append(row)
            added += 1
        os.makedirs(IMPORT, exist_ok=True)
        shutil.move(path, os.path.join(IMPORT, os.path.basename(path)))
        print(f"Imported {added} of {len(data)} messages ({os.path.basename(path)})")

    tmp = DB + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        for m in sorted(rows, key=lambda m: m["date"]):
            f.write(json.dumps(m, ensure_ascii=False) + "\n")
    os.replace(tmp, DB)


main()
