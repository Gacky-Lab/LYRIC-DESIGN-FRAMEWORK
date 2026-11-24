#!/usr/bin/env python3
"""Author-supplied Japanese lyrics -> versioned local JSON handoff (not a Suno API)."""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SONG_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,79}$")
VERSION_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")


def canonical_text(value):
    if not isinstance(value, str):
        raise ValueError("lyrics_text must be a string")
    text = value.replace("\r\n", "\n").replace("\r", "\n")
    if not text.strip() or "\x00" in text or text.startswith("\ufeff"):
        raise ValueError("lyrics must be nonempty UTF-8 without NUL or BOM")
    if len(text.encode("utf-8")) > 1000000:
        raise ValueError("lyrics exceed 1 MB UTF-8 limit")
    return text


def validate_handoff(p):
    required = {"contract_version", "song_id", "lyric_version_id", "language", "lyrics_text", "lyrics_sha256"}
    allowed = required | {"editorial_assessment"}
    if not isinstance(p, dict) or not required <= set(p) or set(p) - allowed:
        raise ValueError("missing or unknown handoff keys")
    if p["contract_version"] != "1.0.0" or p["language"] != "ja":
        raise ValueError("unsupported handoff version/language")
    if not isinstance(p["song_id"], str) or not SONG_ID.fullmatch(p["song_id"]):
        raise ValueError("invalid song_id")
    if not isinstance(p["lyric_version_id"], str) or not VERSION_ID.fullmatch(p["lyric_version_id"]):
        raise ValueError("invalid lyric_version_id")
    text = canonical_text(p["lyrics_text"])
    if text != p["lyrics_text"]:
        raise ValueError("handoff text must use LF line endings")
    if hashlib.sha256(text.encode("utf-8")).hexdigest() != p["lyrics_sha256"]:
        raise ValueError("lyrics SHA-256 mismatch")
    if "editorial_assessment" in p:
        a = p["editorial_assessment"]
        if not isinstance(a, dict) or a.get("method") != "editorial_weighted_1_to_5":
            raise ValueError("invalid editorial method")
        if a.get("evidence_status") != "author_editorial_not_listener_validated":
            raise ValueError("editorial evidence must not imply a listener result")
        complete, score = a.get("complete"), a.get("score_100")
        if type(complete) is not bool:
            raise ValueError("editorial complete must be a boolean")
        if (complete and (type(score) not in (int, float) or not 20 <= score <= 100)
                or not complete and score is not None):
            raise ValueError("invalid editorial score")
    return p


def make_handoff(lyrics, song_id, version_id, card=None):
    if not isinstance(song_id, str) or not SONG_ID.fullmatch(song_id):
        raise ValueError("invalid song_id")
    if not isinstance(version_id, str) or not VERSION_ID.fullmatch(version_id):
        raise ValueError("invalid version ID")
    text = canonical_text(lyrics)
    p = {
        "contract_version": "1.0.0", "song_id": song_id,
        "lyric_version_id": version_id, "language": "ja",
        "lyrics_text": text, "lyrics_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest()
    }
    if card is not None:
        if not isinstance(card, dict) or card.get("song_id") != song_id or card.get("lyric_version_id") != version_id:
            raise ValueError("scorecard song/version identifiers do not match")
        if card.get("assessment_type") != "lyric":
            raise ValueError("vocal score cannot be attached as lyric assessment")
        from scorecard import score_card
        rubric = json.loads((ROOT / "config/rubric.json").read_text(encoding="utf-8"))
        outcome = score_card(card, rubric)
        p["editorial_assessment"] = {
            "method": "editorial_weighted_1_to_5", "complete": outcome["complete"],
            "score_100": outcome["score_100"], "rubric_version": rubric["framework_version"],
            "evidence_status": "author_editorial_not_listener_validated"
        }
    return validate_handoff(p)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lyrics", type=Path, required=True)
    parser.add_argument("--song-id", required=True)
    parser.add_argument("--version-id", required=True)
    parser.add_argument("--scorecard", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        text = args.lyrics.read_text(encoding="utf-8-sig")
        card = json.loads(args.scorecard.read_text(encoding="utf-8")) if args.scorecard else None
        payload = make_handoff(text, args.song_id, args.version_id, card)
        serialized = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(serialized, encoding="utf-8")
            print("Wrote verified lyric handoff:", args.output)
        else:
            print(serialized, end="")
        return 0
    except (OSError, ValueError, UnicodeError, json.JSONDecodeError, KeyError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
