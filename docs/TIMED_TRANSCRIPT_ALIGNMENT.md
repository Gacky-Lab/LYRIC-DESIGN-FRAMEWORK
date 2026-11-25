# Timed transcript alignment candidate

`python scripts/align_transcript.py --lyrics handoff.json --transcript transcript.json --output candidate.json`

The transcript envelope uses schema_version 0.1.0, master_sha256, source (SYNTHETIC_FIXTURE, EXTERNAL_ASR_UNVERIFIED or HUMAN_TRANSCRIPT_UNVERIFIED), and ordered segments with integer start_ms/end_ms and text. It can group multiple segments into each lyric line when normalized Japanese text matches exactly. It rejects mismatches, overlap, unmatched material and segments crossing line boundaries. It does not perform ASR, validate the actual audio or infer pronunciation. Hash linkage is an identity assertion to be checked against the WAV by the consumer.

The output is CANDIDATE_REVIEW_REQUIRED, not approved timing; the video preview refuses this state. A human must check the audio and timing independently before supplying the approved timing contract. No singing recognition or real-song alignment accuracy claim.
