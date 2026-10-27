#!/usr/bin/env python3
"""Imports group history from Telegram Desktop (Export chat history → JSON) into messages.jsonl.

Looks for the newest ChatExport_*/result.json in ~/Downloads or in the bot folder
(or takes the path to result.json as the first argument). Duplicates are skipped.
"""
import glob, json, os, shutil, sys

OUT = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(OUT, "messages.jsonl")
FILES = os.path.join(OUT, "files")
GROUP = json.load(open(os.path.join(OUT, "config.json"), encoding="utf-8"))["group"]


def flat(text):
    if isinstance(text, str):
        return text
    return "".join(t if isinstance(t, str) else t.get("text", "") for t in text)


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        found = glob.glob(os.path.expanduser("~/Downloads/**/ChatExport_*/result.json"), recursive=True)
        found += glob.glob(os.path.join(OUT, "**/ChatExport_*/result.json"), recursive=True)
        if not found:
            sys.exit("ChatExport_*/result.json not found in ~/Downloads or the bot folder.")
        path = max(found, key=os.path.getmtime)
    export = json.load(open(path, encoding="utf-8"))
    base = os.path.dirname(path)

    existing, gid = set(), None
    if os.path.exists(DB):
        for line in open(DB, encoding="utf-8"):
            m = json.loads(line)
            existing.add((m["date"], m["text"]))
            if m.get("chat") == GROUP:
                gid = m["chat_id"]
    if gid is None:  # the Desktop export has the id without the -100 prefix
        gid = int(f"-100{export['id']}")

    added = 0
    os.makedirs(FILES, exist_ok=True)
    with open(DB, "a", encoding="utf-8") as f:
        for m in export.get("messages", []):
            if m.get("type") != "message":
                continue
            date, text = int(m["date_unixtime"]), flat(m.get("text", ""))
            src = m.get("file") or m.get("photo") or ""
            name = ""
            if src and not src.startswith("("):  # "(File not included…)" — the file was not exported
                name = f"{date}_{m['id']}_{os.path.basename(src)}"
                try:
                    shutil.copy(os.path.join(base, src), os.path.join(FILES, name))
                except OSError:
                    name = ""
            if (not text and not name) or (date, text) in existing:
                continue
            existing.add((date, text))
            f.write(json.dumps({"date": date, "chat_id": gid, "chat": GROUP, "who": m.get("from") or "?",
                                "text": text, "file": name}, ensure_ascii=False) + "\n")
            added += 1
    print(f"Imported {added} messages from {path}")


main()
