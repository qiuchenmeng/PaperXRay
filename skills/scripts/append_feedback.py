#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Append one feedback record to the current user's reference.json without
# modifying the shared seed data shipped with the skill.
#
# Examples:
#   python append_feedback.py --query "Q" --positive "A" --negative "B" --preference "P" --scope "equation questions"
#   python append_feedback.py --json <json-string>
#   python append_feedback.py --file record.json
#   python append_feedback.py --list
#   python append_feedback.py --init
#   python append_feedback.py --query "Q" --positive "A" --dry-run
#
# Format is preserved: UTF-8 (with BOM only if the original had one), the
# original newline style (CRLF or LF), 2-space indent, and the leading and
# trailing whitespace around the JSON body.

import argparse
import codecs
import json
import os
from pathlib import Path
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CR = chr(13)
LF = chr(10)
SKILL_DIR = Path(__file__).resolve().parent.parent
BUNDLED_REFERENCE = SKILL_DIR / "data" / "reference.json"
PERSONALIZED_PROMPT_NAME = "runtime-prompt-personalized.md"


def user_state_dir():
    """Return this user's state directory, independent of the installed plugin."""
    override = os.environ.get("PAPERXRAY_HOME", "").strip()
    if override:
        return Path(os.path.expandvars(os.path.expanduser(override))).resolve()
    return Path.home() / ".paperxray"


def ensure_user_reference():
    """Initialize a private copy of the bundled examples without overwriting it."""
    state_dir = user_state_dir()
    state_dir.mkdir(parents=True, exist_ok=True)
    target = state_dir / "reference.json"
    if not target.exists():
        try:
            with target.open("xb") as out:
                out.write(BUNDLED_REFERENCE.read_bytes())
                out.flush()
                os.fsync(out.fileno())
        except FileExistsError:
            # Another session initialized this user's profile concurrently.
            pass
    return target


def load_document(path):
    with open(path, "rb") as fh:
        raw = fh.read()
    bom = raw.startswith(codecs.BOM_UTF8)
    text = raw.decode("utf-8-sig")
    return raw, text, bom


def normalise(value):
    if value is None:
        return []
    if isinstance(value, str):
        value = [value]
    return [str(item).strip() for item in value if str(item).strip()]


def make_record(payload):
    if not isinstance(payload, dict):
        raise ValueError("record must be a JSON object")
    query = str(payload.get("user_query", "")).strip()
    if not query:
        raise ValueError("user_query must not be empty")
    record = {
        "user_query": query,
        "positive": normalise(payload.get("positive")),
        "negative": normalise(payload.get("negative")),
        "preference": str(payload.get("preference", "")).strip(),
    }
    scope = str(payload.get("scope", "")).strip()
    if scope:
        record["scope"] = scope
    return record


def serialise(text, doc, bom):
    newline = CR + LF if (CR + LF) in text else LF
    prefix = text[:len(text) - len(text.lstrip())]
    suffix = text[len(text.rstrip()):]
    body = json.dumps(doc, ensure_ascii=False, indent=2)
    if newline == CR + LF:
        body = body.replace(LF, CR + LF)
    raw = (prefix + body + suffix).encode("utf-8")
    if bom:
        raw = codecs.BOM_UTF8 + raw
    return raw


def write_atomic(path, data):
    d = os.path.dirname(os.path.abspath(path))
    fd, tmp = tempfile.mkstemp(dir=d, suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.remove(tmp)
        raise


def build_record_from_args(args):
    return {
        "user_query": args.query or "",
        "positive": args.positive or [],
        "negative": args.negative or [],
        "preference": args.preference or "",
        "scope": args.scope or "",
    }


def resolve_record(args):
    if args.feed_json is not None:
        return json.loads(args.feed_json)
    if args.file is not None:
        with open(args.file, "r", encoding="utf-8-sig") as fh:
            return json.load(fh)
    return build_record_from_args(args)


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Manage feedback in the current user's PaperXRay state directory."
    )
    parser.add_argument(
        "--path",
        help="explicit reference.json path (defaults to PAPERXRAY_HOME or ~/.paperxray)",
    )
    parser.add_argument(
        "--init",
        action="store_true",
        help="initialize the user's private feedback file and print state paths",
    )
    parser.add_argument("--query", help="user_query")
    parser.add_argument("--positive", action="append", default=[], help="repeatable")
    parser.add_argument("--negative", action="append", default=[], help="repeatable")
    parser.add_argument("--preference", default="", help="one-line preference rule")
    parser.add_argument("--scope", default="", help="intent / condition where the preference applies")
    parser.add_argument("--json", dest="feed_json", help="a full record as a JSON string")
    parser.add_argument("--file", help="path to a JSON file holding one record")
    parser.add_argument("--dry-run", action="store_true", help="validate and show, do not write")
    parser.add_argument("--list", action="store_true", help="list existing records and exit")
    args = parser.parse_args(argv)

    path = args.path or str(ensure_user_reference())
    if args.init:
        _, text, _ = load_document(path)
        doc = json.loads(text)
        records = doc.get("feedback")
        if not isinstance(records, list):
            raise SystemExit("reference.json has no feedback list")
        state_dir = Path(path).resolve().parent
        print("PAPERXRAY_HOME:", state_dir)
        print("reference:", Path(path).resolve())
        print("personalized_prompt:", state_dir / PERSONALIZED_PROMPT_NAME)
        print("feedback_records:", len(records))
        return 0

    text, bom = load_document(path)[1:]
    doc = json.loads(text)
    records = doc.get("feedback")
    if not isinstance(records, list):
        raise SystemExit("reference.json has no feedback list")

    if args.list:
        for i, rec in enumerate(records):
            print(i, rec.get("user_query", ""))
        return 0

    record = make_record(resolve_record(args))
    records.append(record)
    data = serialise(text, doc, bom)

    if args.dry_run:
        print(json.dumps(record, ensure_ascii=False, indent=2))
        print("dry-run: not written; total would be", len(records))
        return 0

    write_atomic(path, data)
    print("appended; total records:", len(records))
    return 0


def entry():
    try:
        return main()
    except ValueError as exc:
        print("error:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(entry())
