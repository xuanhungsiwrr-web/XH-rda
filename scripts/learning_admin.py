"""Operator-only learning approval. Host must enforce authorization outside model tools."""
import argparse
import json
from pathlib import Path
from xh_learning import learning_action

if __name__ == '__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['approve','deprecate'])
    ap.add_argument('--data',required=True,help='Operator-authored approval JSON with exact candidate hash and approval reference')
    args=ap.parse_args()
    print(json.dumps(learning_action(args.action,json.loads(Path(args.data).read_text(encoding='utf-8-sig'))),ensure_ascii=False,indent=2))
