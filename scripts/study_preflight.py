#!/usr/bin/env python3
"""Classify lyric A/B study design. Never infer real listener effectiveness."""
import argparse
import json
import sys
from pathlib import Path

CONTROLS = ("melody_fixed", "vocal_fixed", "arrangement_fixed",
            "tempo_fixed", "loudness_fixed", "source_files_verified")
REQUIRED = {"plan_version", "experiment_id", "song_id", "lyric_a_version",
            "lyric_b_version", "comparison_type", "consent_planned",
            "random_order_planned", "primary_outcome_predeclared", "audio_controls",
            "measurement_state"}


def classify(plan):
    if not isinstance(plan, dict) or set(plan) != REQUIRED:
        raise ValueError("unknown or missing study plan fields")
    if plan["plan_version"] != "1.0.0" or plan["measurement_state"] != "NOT_RUN":
        raise ValueError("unverified study may only be described as NOT_RUN")
    for name in ("experiment_id", "song_id", "lyric_a_version", "lyric_b_version"):
        if not isinstance(plan[name], str) or not plan[name].strip():
            raise ValueError(name + " must be non-empty text")
    if plan["lyric_a_version"] == plan["lyric_b_version"]:
        raise ValueError("A and B must have different lyric versions")
    mode = plan["comparison_type"]
    if mode not in ("text_only", "lyrics_only_audio", "composite_audio"):
        raise ValueError("unknown comparison_type")
    for name in ("consent_planned", "random_order_planned", "primary_outcome_predeclared"):
        if type(plan[name]) is not bool:
            raise ValueError(name + " must be boolean")
    controls = plan["audio_controls"]
    if not isinstance(controls, dict) or set(controls) != set(CONTROLS) or any(
            type(controls[x]) is not bool for x in CONTROLS):
        raise ValueError("audio_controls must contain six explicit booleans")

    missing = []
    if not plan["consent_planned"]:
        missing.append("participant_consent")
    if not plan["random_order_planned"]:
        missing.append("randomized_presentation")
    if not plan["primary_outcome_predeclared"]:
        missing.append("primary_outcome_registered")
    if mode == "lyrics_only_audio":
        missing += [key for key in CONTROLS if not controls[key]]

    if mode == "composite_audio":
        scope = "COMPOSITE_AUDIO_ONLY"
        claim = "Composite music difference; lyric-only causal effect forbidden"
    elif mode == "text_only":
        scope = "TEXT_ONLY"
        claim = "Text-only response; no singing/voice/acoustic effect claim"
    else:
        scope = "LYRICS_ONLY_AUDIO_IF_CONTROLS_ACTUALLY_HOLD"
        claim = "Controls are plan assertions, not measured equivalence"

    state = "NEEDS_CONTROLS_OR_ETHICS" if missing else "READY_FOR_PILOT_REVIEW"
    return {
        "preflight_state": state, "scope": scope, "missing": missing,
        "claim_limit": claim,
        "measurement_state": "NOT_RUN",
        "listener_effect_observed": False,
        "note": "A ready study plan is not evidence of improved lyrics or successful listening research."
    }


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--plan", required=True, type=Path)
    p.add_argument("--output", type=Path)
    a = p.parse_args(argv)
    try:
        result = classify(json.loads(a.plan.read_text(encoding="utf-8")))
        data = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if a.output:
            a.output.parent.mkdir(parents=True, exist_ok=True)
            a.output.write_text(data, encoding="utf-8")
        else:
            print(data, end="")
        return 0
    except (OSError, ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        print("ERROR:", exc, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
