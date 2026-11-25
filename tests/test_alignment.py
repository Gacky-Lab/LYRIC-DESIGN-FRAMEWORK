import unittest
from scripts.align_transcript import align
from scripts.export_handoff import make_handoff

class AlignmentTests(unittest.TestCase):
    def setUp(self):
        self.h=make_handoff("朝の光\n青い空\n","fixture","v1")
        self.t={"schema_version":"0.1.0","master_sha256":"a"*64,"source":"SYNTHETIC_FIXTURE","segments":[{"start_ms":0,"end_ms":500,"text":"朝の"},{"start_ms":600,"end_ms":900,"text":"光。"},{"start_ms":1100,"end_ms":2000,"text":"青い空"}]}
    def test_match(self):
        r=align(self.h,self.t)
        self.assertEqual(r["review_status"],"CANDIDATE_REVIEW_REQUIRED")
        self.assertEqual(r["cues"],[{"start_ms":0,"end_ms":900,"line_index":0},{"start_ms":1100,"end_ms":2000,"line_index":1}])
        self.assertFalse(r["pronunciation_verified"])
    def test_wrong_text(self):
        self.t["segments"][1]["text"]="闇"
        with self.assertRaises(ValueError): align(self.h,self.t)
    def test_overlap(self):
        self.t["segments"][1]["start_ms"]=400
        with self.assertRaises(ValueError): align(self.h,self.t)
    def test_extra_segment(self):
        self.t["segments"].append({"start_ms":2100,"end_ms":2200,"text":"余分"})
        with self.assertRaises(ValueError): align(self.h,self.t)
