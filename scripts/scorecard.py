#!/usr/bin/env python3
"""Small reference scoring checker, not a prediction model. Standard library only."""
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / 'config' / 'rubric.json'

def score_card(payload, config):
    kind = payload.get('assessment_type')
    if kind not in ('lyric', 'vocal'):
        raise ValueError('assessment_type must be lyric or vocal')
    dims = config[kind]['dimensions']
    expected = {d['id'] for d in dims}
    scores = payload.get('scores')
    if not isinstance(scores, dict):
        raise ValueError('scores must be an object')
    unknown = set(scores) - expected
    missing = expected - set(scores)
    if unknown or missing:
        raise ValueError(f'Unknown keys: {sorted(unknown)} / missing: {sorted(missing)}')
    total=0.0
    unrated=[]
    for d in dims:
        v=scores[d['id']]
        if v is None:
            unrated.append(d['label_ja'])
            continue
        if isinstance(v, bool) or not isinstance(v, (int,float)) or not (1<=v<=5):
            raise ValueError(f'{d["id"]}: rating must be 1..5 or null')
        total += d['weight'] * v/5
    return {'kind':kind, 'complete': not unrated, 'score_100': round(total,2) if not unrated else None, 'unrated_dimensions':unrated, 'note':'編集用採点。実聴・リスナー検証やヒット確率ではありません。'}

def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('scorecard', type=Path)
    args=p.parse_args(argv)
    try:
        config=json.loads(CONFIG.read_text(encoding='utf-8'))
        payload=json.loads(args.scorecard.read_text(encoding='utf-8'))
        result=score_card(payload,config)
    except (ValueError, OSError, json.JSONDecodeError, KeyError) as exc:
        print(f'ERROR: {exc}',file=sys.stderr)
        return 2
    print(json.dumps(result,ensure_ascii=False,indent=2))
    return 0

if __name__=='__main__':
    raise SystemExit(main())
