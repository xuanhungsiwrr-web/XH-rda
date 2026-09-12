"""Operator release gate: approved lesson -> CR -> real regressions -> version receipt."""
import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path
from xh_core import PLUGIN, encoded, digest, stamp
from xh_learning import Learning

def fingerprint(root=PLUGIN):
    files=[]
    for folder in ['scripts','skills','references','workflows','tests']:
        files += [p for p in (root/folder).rglob('*') if p.is_file() and '__pycache__' not in p.parts]
    return digest(encoded({p.relative_to(root).as_posix():digest(p.read_bytes()) for p in sorted(files)}))

def change(kb, cr_id):
    r=kb.db.execute('SELECT data FROM changes WHERE id=?',(cr_id,)).fetchone()
    if not r: raise ValueError('Unknown change request')
    cr=json.loads(r[0]); lesson=kb.get(cr['lesson_id'])
    if lesson['status']!='approved' or lesson['content_hash']!=cr['lesson_hash']:
        raise ValueError('Lesson is no longer approved/current')
    return cr

def test_change(kb, cr_id):
    cr=change(kb,cr_id)
    before=fingerprint()
    result=subprocess.run([sys.executable,'-X','utf8','-m','unittest','discover','-s','tests','-v'],
        cwd=PLUGIN,env={**os.environ,'PYTHONUTF8':'1'},capture_output=True,text=True,encoding='utf-8',timeout=180)
    cases=kb.evaluate()
    if result.returncode or not cases['passed'] or fingerprint()!=before:
        raise ValueError('Regression failed or source changed during test: '+result.stderr[-2500:])
    cr.update(status='tested', test={'at':stamp(),'source_hash':before,
        'cases_hash':digest(encoded(cases['cases'])), 'output':result.stderr[-8000:]})
    kb.db.execute('BEGIN IMMEDIATE')
    return kb.save(cr,'tested','regression-runner','changes')

def release(kb, cr_id, version, actor, approval_reference):
    cr=change(kb,cr_id)
    if cr['status'] not in ['tested','release-authorized'] or cr['test']['source_hash']!=fingerprint():
        raise ValueError('Run regressions on exact current source before release')
    cases=kb.evaluate()
    if not cases['passed'] or digest(encoded(cases['cases']))!=cr['test']['cases_hash']:
        raise ValueError('Evaluation cases changed; rerun tests')
    if cr['status']=='release-authorized':
        if cr['release'] == {'version':version,'actor':actor,'reference':approval_reference}:
            return cr
        raise ValueError('Different release intent requires a new test run')
    if not re.fullmatch(r'\d+\.\d+\.\d+',version) or not actor or not approval_reference:
        raise ValueError('Semantic version and explicit operator release approval required')
    current=json.loads((PLUGIN/'.claude-plugin/plugin.json').read_text(encoding='utf-8-sig'))['version']
    if tuple(map(int,version.split('.'))) <= tuple(map(int,current.split('.'))):
        raise ValueError('New version must exceed installed manifest version')
    cr.update(status='release-authorized',release={'version':version,'actor':actor,'reference':approval_reference})
    kb.db.execute('BEGIN IMMEDIATE')
    return kb.save(cr,'release_authorized',actor,'changes')

if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action',choices=['test','release'])
    ap.add_argument('--data',required=True)
    a=ap.parse_args(); data=json.loads(Path(a.data).read_text(encoding='utf-8-sig'))
    with Learning() as kb:
        print(json.dumps((test_change if a.action=='test' else release)(kb,**data),ensure_ascii=False,indent=2))
