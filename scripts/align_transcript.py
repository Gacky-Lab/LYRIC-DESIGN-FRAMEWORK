"""Conservative exact line alignment from externally timestamped transcript evidence, not ASR."""
import argparse
import hashlib
import json
import re
import unicodedata
from pathlib import Path
try:
    from .export_handoff import validate_handoff
except ImportError:
    from export_handoff import validate_handoff

def normalize(s):
    if not isinstance(s,str): raise ValueError("text must be a string")
    return "".join(c for c in unicodedata.normalize("NFKC",s) if not c.isspace() and not unicodedata.category(c).startswith("P"))

def align(handoff, transcript):
    validate_handoff(handoff)
    if not isinstance(transcript,dict) or transcript.get("schema_version")!="0.1.0":
        raise ValueError("invalid transcript schema")
    master=transcript.get("master_sha256")
    if not isinstance(master,str) or not re.fullmatch("[0-9a-f]{64}",master):
        raise ValueError("invalid master identity")
    segments=transcript.get("segments")
    if not isinstance(segments,list) or not 1<=len(segments)<=4000:
        raise ValueError("invalid segments")
    source=transcript.get("source")
    if source not in ("SYNTHETIC_FIXTURE","EXTERNAL_ASR_UNVERIFIED","HUMAN_TRANSCRIPT_UNVERIFIED"):
        raise ValueError("unsupported transcript provenance")
    prepared=[]; previous=0
    for s in segments:
        a,b=s.get("start_ms"),s.get("end_ms")
        if type(a) is not int or type(b) is not int or not 0<=a<b<=600000 or a<previous:
            raise ValueError("invalid timestamp order")
        text=normalize(s.get("text"))
        if not text or len(text)>1000: raise ValueError("empty or oversized normalized segment")
        prepared.append((a,b,text)); previous=b
    cues=[]; k=0
    for i,line in enumerate(handoff["lyrics_text"].split("\n")):
        target=normalize(line)
        if not target: continue
        start=k; combined=""
        while k<len(prepared) and len(combined)<len(target):
            combined+=prepared[k][2]; k+=1
            if not target.startswith(combined): raise ValueError("transcript differs from lyric line")
        if combined!=target: raise ValueError("line not fully matched")
        cues.append({"start_ms":prepared[start][0],"end_ms":prepared[k-1][1],"line_index":i})
    if k!=len(prepared) or not cues: raise ValueError("unmatched transcript material")
    return {"schema_version":"0.1.0","master_sha256":master,"lyrics_sha256":handoff["lyrics_sha256"],"lyric_version_id":handoff["lyric_version_id"],"review_status":"CANDIDATE_REVIEW_REQUIRED","transcript_source":source,"method":"ordered-exact-normalized-segments","cues":cues,"pronunciation_verified":False}

def load(p):
    with p.open("rb") as f: data=f.read(1024*1024+1)
    if len(data)>1024*1024: raise ValueError("input too large")
    return json.loads(data)
def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--lyrics",type=Path,required=True); p.add_argument("--transcript",type=Path,required=True); p.add_argument("--output",type=Path,required=True)
    a=p.parse_args()
    try:
        r=align(load(a.lyrics),load(a.transcript))
        with a.output.open("x",encoding="utf-8") as f: json.dump(r,f,ensure_ascii=False,indent=2,allow_nan=False)
    except (ValueError,OSError,TypeError,AttributeError) as e: p.exit(2,f"ERROR: {e}\n")
if __name__=="__main__": main()
