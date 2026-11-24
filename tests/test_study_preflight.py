"""Fail-closed study preflight; no invented listener outcomes."""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from study_preflight import classify

BASE = json.loads((ROOT / "examples/study_preflight/unfinished_lyrics_only_plan.json").read_text(encoding="utf-8"))


class StudyPlanTests(unittest.TestCase):
    def test_unfinished_lyrics_only_is_not_ready(self):
        state = classify(BASE)
        self.assertEqual(state["preflight_state"], "NEEDS_CONTROLS_OR_ETHICS")
        self.assertIn("vocal_fixed", state["missing"])
        self.assertFalse(state["listener_effect_observed"])

    def test_fully_controlled_plan_still_not_a_result(self):
        p = copy.deepcopy(BASE)
        p["consent_planned"] = p["random_order_planned"] = p["primary_outcome_predeclared"] = True
        p["audio_controls"] = {k: True for k in p["audio_controls"]}
        result = classify(p)
        self.assertEqual(result["preflight_state"], "READY_FOR_PILOT_REVIEW")
        self.assertEqual(result["measurement_state"], "NOT_RUN")

    def test_composite_audio_never_claims_lyric_only_effect(self):
        p = copy.deepcopy(BASE)
        p["comparison_type"] = "composite_audio"
        p["consent_planned"] = p["random_order_planned"] = p["primary_outcome_predeclared"] = True
        result = classify(p)
        self.assertEqual(result["scope"], "COMPOSITE_AUDIO_ONLY")
        self.assertIn("forbidden", result["claim_limit"])

    def test_text_only_does_not_require_melody_fixed(self):
        p = copy.deepcopy(BASE)
        p["comparison_type"] = "text_only"
        p["consent_planned"] = p["random_order_planned"] = p["primary_outcome_predeclared"] = True
        self.assertEqual(classify(p)["preflight_state"], "READY_FOR_PILOT_REVIEW")
        self.assertEqual(classify(p)["scope"], "TEXT_ONLY")

    def test_reject_fabricated_pass_state(self):
        p = copy.deepcopy(BASE)
        p["measurement_state"] = "PASS"
        with self.assertRaises(ValueError):
            classify(p)

    def test_reject_same_a_b(self):
        p = copy.deepcopy(BASE)
        p["lyric_b_version"] = p["lyric_a_version"]
        with self.assertRaises(ValueError):
            classify(p)

    def test_reject_non_boolean(self):
        p = copy.deepcopy(BASE)
        p["audio_controls"]["vocal_fixed"] = "true"
        with self.assertRaises(ValueError):
            classify(p)

    def test_reject_unknown_fields(self):
        p = copy.deepcopy(BASE)
        p["listener_success_rate"] = 100
        with self.assertRaises(ValueError):
            classify(p)

    def test_all_samples_keep_measurement_not_run(self):
        for path in (ROOT / "examples/study_preflight").glob("*.json"):
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(classify(data)["measurement_state"], "NOT_RUN")

    def test_schema_matches_examples_if_jsonschema_installed(self):
        try:
            from jsonschema import Draft202012Validator
        except ImportError:
            self.skipTest("jsonschema is optional")
        schema = json.loads((ROOT / "schemas/study_plan.v1.schema.json").read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        for path in (ROOT / "examples/study_preflight").glob("*.json"):
            Draft202012Validator(schema).validate(json.loads(path.read_text(encoding="utf-8")))
