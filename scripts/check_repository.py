#!/usr/bin/env python3
"""Repository integrity checks; no third-party dependencies or remote requests."""
import csv
import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_LINK = re.compile(r'!?\[[^\]\n]*\]\(([^)]+)\)')
CSV_TEMPLATES = (
    'templates/ab-plan.template.csv',
    'templates/change-log.template.csv',
    'templates/listener-response.template.csv',
)


def check():
    failures = []
    config = json.loads((ROOT / 'config/rubric.json').read_text(encoding='utf-8'))
    for kind, expected_count in (('lyric', 8), ('vocal', 6)):
        block = config[kind]
        dims = block['dimensions']
        ids = [d['id'] for d in dims]
        weights = [d['weight'] for d in dims]
        if len(dims) != expected_count or len(set(ids)) != len(ids):
            failures.append(f'{kind}: unexpected/duplicate dimensions')
        if any(isinstance(w, bool) or not isinstance(w, (int, float)) or w <= 0 for w in weights):
            failures.append(f'{kind}: invalid weight')
        if sum(weights) != block['total_weight'] or sum(weights) != 100:
            failures.append(f'{kind}: weights must total 100')
        template_path = ROOT / f'templates/{"scorecard" if kind == "lyric" else "vocal-scorecard"}.template.json'
        card = json.loads(template_path.read_text(encoding='utf-8'))
        if card['assessment_type'] != kind or set(card['scores']) != set(ids):
            failures.append(f'{kind}: template axes do not match rubric')
        if any(value is not None for value in card['scores'].values()):
            failures.append(f'{kind}: new template must be unrated')

    for path in ROOT.rglob('*.json'):
        try:
            json.loads(path.read_text(encoding='utf-8'))
        except (ValueError, UnicodeError) as exc:
            failures.append(f'{path.relative_to(ROOT)}: invalid JSON: {exc}')

    for path in ROOT.rglob('*.md'):
        content = path.read_text(encoding='utf-8')
        for match in MARKDOWN_LINK.finditer(content):
            raw = match.group(1).strip().split(' "', 1)[0].strip('<>')
            if not raw or raw.startswith(('#', 'mailto:', 'data:')):
                continue
            if urlsplit(raw).scheme or raw.startswith('//'):
                continue
            target = unquote(urlsplit(raw).path)
            if not target or not (path.parent / target).exists():
                failures.append(f'{path.relative_to(ROOT)}: broken link {raw}')

    for name in CSV_TEMPLATES:
        with (ROOT / name).open(encoding='utf-8', newline='') as f:
            columns = next(csv.reader(f), [])
        if not columns or len(set(columns)) != len(columns):
            failures.append(f'{name}: empty or duplicate CSV column')

    for name in ('improvement.md', 'validation.md'):
        path = ROOT / '.github' / 'ISSUE_TEMPLATE' / name
        content = path.read_text(encoding='utf-8')
        if not content.startswith('---\n') or '\n---\n' not in content[4:]:
            failures.append(f'{path.relative_to(ROOT)}: invalid Issue template front matter')

    return failures


def main():
    failures = check()
    if failures:
        for item in failures:
            print('FAIL:', item, file=sys.stderr)
        return 1
    print('PASS: rubric, JSON, templates, Markdown links and Issue front matter')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
