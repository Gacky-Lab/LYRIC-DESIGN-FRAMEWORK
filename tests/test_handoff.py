import hashlib
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from export_handoff import canonical_text, make_handoff, validate_handoff


class HandoffTests(unittest.TestCase):
    def test_utf8_hash(self):
        p = make_handoff("今日は\n晴れた\n", "demo_01", "v1")
        self.assertEqual(p["lyrics_sha256"], hashlib.sha256("今日は\n晴れた\n".encode("utf-8")).hexdigest())

    def test_windows_newlines(self):
        p = make_handoff("一行\r\n二行\r\n", "demo_01", "v1")
        self.assertEqual(p["lyrics_text"], "一行\n二行\n")

    def test_preserves_spaces(self):
        self.assertEqual(make_handoff(" 朝 \n", "x", "v1")["lyrics_text"], " 朝 \n")

    def test_reject_tampering(self):
        p = make_handoff("あ", "demo_01", "v1")
        p["lyrics_text"] += "い"
        with self.assertRaises(ValueError):
            validate_handoff(p)

    def test_reject_empty_bom_nul(self):
        for value in ("", " \n ", "\ufeffあ", "\x00"):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                canonical_text(value)

    def test_reject_bad_ids(self):
        for value in ("../secret", "a space", "日本語"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                make_handoff("あ", value, "v1")

    def test_editorial_assessment_is_not_listener_data(self):
        card = json.loads((ROOT / "examples/fictional-revision/scorecard-B.json").read_text(encoding="utf-8"))
        p = make_handoff("あ", card["song_id"], card["lyric_version_id"], card)
        self.assertEqual(p["editorial_assessment"]["score_100"], 76)
        self.assertEqual(p["editorial_assessment"]["evidence_status"], "author_editorial_not_listener_validated")

    def test_scorecard_version_mismatch(self):
        card = json.loads((ROOT / "examples/fictional-revision/scorecard-B.json").read_text(encoding="utf-8"))
        with self.assertRaises(ValueError):
            make_handoff("あ", card["song_id"], "wrong-version", card)

    def test_unknown_version(self):
        p = make_handoff("あ", "demo", "v1")
        p["contract_version"] = "2.0.0"
        with self.assertRaises(ValueError):
            validate_handoff(p)

    def test_json_schema_when_available(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("optional jsonschema dependency unavailable")
        schema = json.loads((ROOT / "schemas/lyric_handoff.v1.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(make_handoff("あ\n", "demo", "v1"))
