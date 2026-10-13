#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Append one feedback record to data/reference.json without breaking its format.
#
# Examples:
#   python append_feedback.py --query "Q" --positive "A" --negative "B" --preference "P"
#   python append_feedback.py --json <json-string>
#   python append_feedback.py --file record.json
#   python append_feedback.py --list
#   python append_feedback.py --query "Q" --positive "A" --dry-run
#
# Format is preserved: UTF-8 (with BOM only if the original had one), the
# original newline style (CRLF or LF), 2-space indent, and the leading and
# trailing whitespace around the JSON body.

import argparse
import codecs
import json
import os
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

CR = chr(13)
LF = chr(10)
DEFAULT_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), os.pardir, "data", "reference.json"
)

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
    return {
        "user_query": query,
        "positive": normalise(payload.get("positive")),
        "negative": normalise(payload.get("negative")),
        "preference": str(payload.get("preference", "")).strip(),
    }


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
        description="Append a feedback record to data/reference.json."
    )
    parser.add_argument("--path", default=DEFAULT_PATH, help="target reference.json")
    parser.add_argument("--query", help="user_query")
    parser.add_argument("--positive", action="append", default=[], help="repeatable")
    parser.add_argument("--negative", action="append", default=[], help="repeatable")
    parser.add_argument("--preference", default="", help="one-line preference rule")
    parser.add_argument("--json", dest="feed_json", help="a full record as a JSON string")
    parser.add_argument("--file", help="path to a JSON file holding one record")
    parser.add_argument("--dry-run", action="store_true", help="validate and show, do not write")
    parser.add_argument("--list", action="store_true", help="list existing records and exit")
    args = parser.parse_args(argv)

    text, bom = load_document(args.path)[1:]
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

    write_atomic(args.path, data)
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
