import json
import unittest
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from scorecard import score_card
config=json.loads((ROOT/'config'/'rubric.json').read_text(encoding='utf-8'))

class ScorecardTests(unittest.TestCase):
    def payload(self, kind, val):
        return {'assessment_type':kind,'scores':{d['id']:val for d in config[kind]['dimensions']}}

    def test_all_five_is_100(self):
        self.assertEqual(score_card(self.payload('lyric',5),config)['score_100'],100)
    def test_all_one_is_20(self):
        self.assertEqual(score_card(self.payload('lyric',1),config)['score_100'],20)
    def test_unrated_is_not_zero(self):
        p=self.payload('lyric',5);p['scores']['scene']=None
        r=score_card(p,config)
        self.assertFalse(r['complete']);self.assertIsNone(r['score_100'])
    def test_vocal_weights(self):
        self.assertEqual(score_card(self.payload('vocal',5),config)['score_100'],100)
    def test_reject_invalid(self):
        p=self.payload('lyric',6)
        with self.assertRaises(ValueError): score_card(p,config)
    def test_reject_unexpected_axis(self):
        p=self.payload('lyric',5);p['scores']['extra']=1
        with self.assertRaises(ValueError): score_card(p,config)

if __name__=='__main__': unittest.main()
