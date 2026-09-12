"""Shared, transactional domain knowledge. No model memory or provider telemetry."""
import json
import os
import re
import sqlite3
from pathlib import Path
from xh_core import PLUGIN, atomic, encoded, digest, stamp, relative

def check_case(record):
    """Deterministic evidence guard; semantic correctness still requires independent review."""
    findings = []
    for fact in record.get('facts', []):
        if not fact.get('source') or not fact.get('quote'): findings.append('missing_source')
        if fact.get('status') == 'conflict': findings.append('conflicting_fact')
        if fact.get('assumption') and not fact.get('labelled_assumption'): findings.append('unlabelled_assumption')
    for legal in record.get('legal', []):
        if not all(legal.get(k) for k in ['original_url','effective_date','checked_at','applicability']):
            findings.append('unverified_legal')
    return sorted(set(findings))

class Learning:
    def __init__(self, root=None):
        self.root = Path(root or os.getenv('XH_TUVAN_KNOWLEDGE_ROOT') or PLUGIN).resolve()
        for folder in ['knowledge/approved','knowledge/candidates','knowledge/rejected','knowledge/deprecated',
                       'learning/evaluation_cases','learning/metrics','learning/change_requests']:
            (self.root/folder).mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(self.root/'learning/registry.sqlite', timeout=20)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''CREATE TABLE IF NOT EXISTS lessons(id TEXT PRIMARY KEY, data TEXT);
            CREATE TABLE IF NOT EXISTS events(seq INTEGER PRIMARY KEY, data TEXT);
            CREATE TABLE IF NOT EXISTS changes(id TEXT PRIMARY KEY, data TEXT);''')
        # Rebuild portable views on open, including recovery after interrupted projection writes.
        self.db.execute('BEGIN IMMEDIATE')
        try: self.project(); self.db.commit()
        except BaseException: self.db.rollback(); self.db.close(); raise

    def __enter__(self): return self
    def __exit__(self, *args): self.db.close()

    def get(self, lid):
        row = self.db.execute('SELECT data FROM lessons WHERE id=?', (lid,)).fetchone()
        if not row: raise ValueError('Unknown lesson')
        return json.loads(row[0])

    def project(self):
        rows = [json.loads(r[0]) for r in self.db.execute('SELECT data FROM lessons ORDER BY id')]
        for row in rows:
            folder = row['status'] if row['status'] in ['approved','rejected','deprecated'] else 'candidates'
            for other in ['approved','candidates','rejected','deprecated']:
                file = self.root/'knowledge'/other/(row['id']+'.json')
                if other == folder: atomic(file, encoded(row))
                elif file.exists(): file.unlink()
        events = [json.loads(r[0]) for r in self.db.execute('SELECT data FROM events ORDER BY seq')]
        atomic(self.root/'learning/LESSONS_LEDGER.jsonl', ''.join(json.dumps(e,ensure_ascii=False)+'\n' for e in events).encode())
        atomic(self.root/'learning/CHANGELOG_LEARNING.md', ('# Learning changelog\n\n'+'\n'.join(
            '- '+e['date']+' '+e['id']+' → '+e['event'] for e in events)+'\n').encode())
        counts = {s:sum(r['status']==s for r in rows) for s in ['candidate','validated','approved','rejected','deprecated']}
        atomic(self.root/'learning/metrics/status.json', encoded(counts))
        for r in self.db.execute('SELECT data FROM changes'):
            cr = json.loads(r[0]); atomic(self.root/'learning/change_requests'/(cr['id']+'.json'), encoded(cr))

    def save(self, row, event, actor, table='lessons'):
        self.db.execute('INSERT OR REPLACE INTO '+table+' VALUES(?,?)', (row['id'], json.dumps(row,ensure_ascii=False)))
        self.db.execute('INSERT INTO events(data) VALUES(?)', (json.dumps({'id':row['id'], 'event':event,
            'actor':actor, 'date':stamp(), 'record':row},ensure_ascii=False),))
        self.db.commit()
        self.db.execute('BEGIN IMMEDIATE')
        try: self.project(); self.db.commit()
        except BaseException: self.db.rollback(); raise
        return row

    def candidate(self, title, rule, evidence, author, scope='domain', category='workflow', risk='normal', cases=None):
        if scope == 'global': return {'destination':'GLOBAL_CONTROL','stored':False}
        if scope != 'domain': raise ValueError('Project facts belong in project/.ai/')
        if category not in ['writing','technical','legal','qa','workflow']: raise ValueError('Not a domain category')
        if risk not in ['normal','high']: raise ValueError('Invalid risk')
        if not all(isinstance(v,str) and v.strip() for v in [title,rule,author]): raise ValueError('Title, rule and author required')
        if not evidence or not cases: raise ValueError('Evidence and regression cases required')
        if not all(isinstance(e,dict) and all(e.get(k) for k in ['reference','quote']) for e in evidence):
            raise ValueError('Each evidence needs reference and quote, sanitized for reuse')
        for case in cases:
            if not isinstance(case.get('input'),dict) or not isinstance(case.get('expected_findings'),list):
                raise ValueError('Case requires input and expected_findings')
            if not case.get('explanation'): raise ValueError('Case needs an explanation of the regression')
        content = dict(title=title,rule=rule,evidence=evidence,scope=scope,category=category,
                       risk='high' if category in ['technical','legal'] else risk,cases=cases)
        lid = 'L-'+digest(encoded(content))[:20]
        self.db.execute('BEGIN IMMEDIATE')
        old = self.db.execute('SELECT data FROM lessons WHERE id=?',(lid,)).fetchone()
        if old: self.db.rollback(); return json.loads(old[0])
        row = {**content,'id':lid,'content_hash':digest(encoded(content)), 'author':author,'status':'candidate'}
        return self.save(row,'candidate',author)

    def validate(self, lesson_id, reviewer, evidence_checked, reusable, conflicts_checked, rationale):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.get(lesson_id)
            if row['status'] != 'candidate': raise ValueError('Only candidate can be validated')
            if not reviewer or reviewer == row['author']: raise ValueError('Independent reviewer required')
            if not all(v is True for v in [evidence_checked,reusable,conflicts_checked]) or not rationale.strip():
                raise ValueError('Evidence, applicability, conflicts and rationale must be reviewed')
            results = [check_case(c['input']) == sorted(set(c['expected_findings'])) for c in row['cases']]
            # A valuable new regression may fail before the approved change is implemented.
            # Validation reviews its expected behavior; release still requires all cases passing.
            row.update(status='validated', validation={'reviewer':reviewer,'rationale':rationale,
                       'content_hash':row['content_hash'], 'case_results':results})
            for i,c in enumerate(row['cases']):
                atomic(self.root/'learning/evaluation_cases'/(lesson_id+'-'+str(i)+'.json'), encoded(c))
            return self.save(row,'validated',reviewer)
        except BaseException: self.db.rollback(); raise

    def approve(self, lesson_id, actor, approval_reference, expected_hash):
        """Operator boundary only. Actor/reference are audit data, not authentication."""
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row = self.get(lesson_id)
            if row['status'] != 'validated' or row['content_hash'] != expected_hash:
                raise ValueError('Approval needs validated exact content hash')
            if not actor or actor in [row['author'],row['validation']['reviewer']] or not approval_reference:
                raise ValueError('Explicit independent operator approval reference required')
            row.update(status='approved', approval={'actor':actor,'reference':approval_reference,'hash':expected_hash})
            return self.save(row,'approved',actor)
        except BaseException: self.db.rollback(); raise

    def disposition(self, lesson_id, actor, reason, status):
        self.db.execute('BEGIN IMMEDIATE')
        try:
            row=self.get(lesson_id)
            allowed = ['candidate','validated'] if status == 'rejected' else ['approved']
            if row['status'] not in allowed or not actor or not reason: raise ValueError('Invalid disposition')
            row.update(status=status, disposition={'actor':actor,'reason':reason})
            return self.save(row,status,actor)
        except BaseException: self.db.rollback(); raise

    def snapshot(self):
        rows=[json.loads(r[0]) for r in self.db.execute('SELECT data FROM lessons ORDER BY id')]
        approved=[r for r in rows if r['status']=='approved']
        return {'snapshot':'KB-'+digest(encoded(approved))[:20], 'lessons':approved,
                'plugin_version':'0.8.0', 'ledger_events':self.db.execute('SELECT count(*) FROM events').fetchone()[0]}

    def change_request(self, lesson_id, paths, actor):
        row=self.get(lesson_id)
        if row['status']!='approved': raise ValueError('Approve lesson before change request')
        if not paths or not actor: raise ValueError('Affected paths and actor required')
        for path in paths:
            relative(PLUGIN,path)
            if not path.startswith(('skills/','references/','scripts/','workflows/')): raise ValueError('Domain files only')
        cr={'id':'CR-'+digest(encoded([lesson_id,sorted(paths)]))[:20], 'lesson_id':lesson_id,
            'paths':paths,'status':'requested','actor':actor,'lesson_hash':row['content_hash']}
        self.db.execute('BEGIN IMMEDIATE')
        old=self.db.execute('SELECT data FROM changes WHERE id=?',(cr['id'],)).fetchone()
        if old: self.db.rollback(); return json.loads(old[0])
        return self.save(cr,'change_requested',actor,'changes')

    def evaluate(self):
        files=sorted((self.root/'learning/evaluation_cases').glob('*.json'))
        results=[]
        required = {}
        for r in self.db.execute('SELECT data FROM lessons'):
            row = json.loads(r[0])
            if 'validation' in row:
                for i, case in enumerate(row['cases']):
                    required[row['id']+'-'+str(i)+'.json'] = digest(encoded(case))
        for file in files:
            c=json.loads(file.read_text(encoding='utf-8'))
            results.append({'case':file.name,'sha256':digest(file.read_bytes()),
                'passed':check_case(c['input'])==sorted(set(c['expected_findings'])) and
                         (file.name not in required or required[file.name] == digest(file.read_bytes()))})
        for missing in sorted(set(required)-{p.name for p in files}):
            results.append({'case':missing,'sha256':None,'passed':False,'reason':'Registered regression case missing'})
        result={'at':stamp(),'passed':bool(results) and all(r['passed'] for r in results),'cases':results,
                'scope':'Deterministic evidence guards; semantic skill quality requires reviewer evaluation.'}
        atomic(self.root/'learning/metrics/evaluation.json',encoded(result))
        return result

def learning_action(action, payload):
    with Learning() as kb:
        actions={'candidate':kb.candidate,'validate':kb.validate,'snapshot':kb.snapshot,
                 'change-request':kb.change_request,'evaluate':kb.evaluate,
                 'approve':kb.approve,
                 'reject':lambda **d:kb.disposition(**d,status='rejected'),
                 'deprecate':lambda **d:kb.disposition(**d,status='deprecated')}
        if action not in actions: raise ValueError('Unknown learning action')
        return actions[action](**payload)
