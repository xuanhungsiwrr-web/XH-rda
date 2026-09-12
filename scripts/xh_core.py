"""Portable report workspace. JSON on disk; SQLite revisions; no provider dependency."""
from __future__ import annotations
import hashlib
import json
import os
from pathlib import Path
import re
import sqlite3
import tempfile
import unicodedata
import uuid
from datetime import datetime, timezone
from xh_layout import PLUGIN_VERSION, LAYOUT_VERSION, detect_layout, ensure_new_layout

PLUGIN = Path(__file__).resolve().parents[1]

def stamp():
    return datetime.now(timezone.utc).isoformat()

def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode('utf-8')

def digest(data):
    return hashlib.sha256(data).hexdigest()

def atomic(path, data):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix='.xh-')
    try:
        with os.fdopen(fd, 'wb') as f:
            f.write(data); f.flush(); os.fsync(f.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)

def relative(root, name):
    # Reject Windows drives/ADS even when tests run on Linux.
    if not name or ':' in str(name) or Path(name).is_absolute():
        raise ValueError('Expected project-relative path')
    p = (Path(root) / name).resolve()
    if not p.is_relative_to(Path(root).resolve()):
        raise ValueError('Path escapes project root')
    return p

def fold(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text.lower().replace('đ', 'd'))
                   if unicodedata.category(c) != 'Mn')

def library(root, query=''):
    """Discovery only. Selection uses explicit files; nothing silently omitted."""
    words = set(re.findall(r'\w+', fold(query)))
    result = []
    for p in sorted(Path(root).glob('*.md')):
        raw = p.read_bytes()
        score = len(words & set(re.findall(r'\w+', fold(p.stem))))
        result.append({'file': p.name, 'sha256': digest(raw), 'bytes': len(raw), 'score': score})
    return sorted(result, key=lambda r: (-r['score'], r['file']))

class Project:
    def __init__(self, root):
        self.root = Path(root).resolve()
        if not (self.root / 'project.json').is_file():
            raise ValueError('Initialize project first')
        self.layout = detect_layout(self.root)
        db_path = self.layout.at(self.root, 'state_db')
        if not db_path.is_file():
            raise ValueError('Workspace state database is missing; run migration preflight or restore the legacy DB')
        self.db = sqlite3.connect(db_path, timeout=20)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS revisions(
          id TEXT PRIMARY KEY, artifact TEXT NOT NULL, hash TEXT NOT NULL,
          path TEXT NOT NULL, origin TEXT NOT NULL, actor TEXT NOT NULL,
          deps TEXT NOT NULL, meta TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS heads(artifact TEXT PRIMARY KEY, revision TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS approvals(revision TEXT PRIMARY KEY, actor TEXT, created TEXT);
        CREATE TABLE IF NOT EXISTS delivery_pairs(
          pair_id TEXT PRIMARY KEY, release_id TEXT UNIQUE NOT NULL,
          output_artifact TEXT NOT NULL, feedback_artifact TEXT NOT NULL,
          output_path TEXT NOT NULL, feedback_path TEXT NOT NULL,
          baseline_hash TEXT NOT NULL, status TEXT NOT NULL,
          plugin_version TEXT NOT NULL, created TEXT NOT NULL, updated TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS feedback_imports(
          pair_id TEXT NOT NULL, feedback_hash TEXT NOT NULL,
          feedback_revision TEXT NOT NULL, analysis_artifact TEXT,
          created TEXT NOT NULL, PRIMARY KEY(pair_id, feedback_hash));
        ''')

    def path(self, key, *parts):
        return self.layout.rel(key, *parts)

    def blob_path(self, content_hash):
        return self.layout.at(self.root, 'artifacts', content_hash)

    def close(self):
        self.db.close()

    @classmethod
    def init(cls, root, metadata=None):
        root = Path(root).resolve()
        if (root / 'project.json').exists():
            p = cls(root); version = p.layout.version; p.close()
            return {'project': str(root), 'existing': True, 'layout_version': version}
        layout = ensure_new_layout(root)
        layout.at(root, 'ai', 'facts').mkdir(parents=True, exist_ok=True)
        layout.at(root, 'ai', 'metadata').mkdir(parents=True, exist_ok=True)
        db = sqlite3.connect(layout.at(root, 'state_db')); db.close()
        config = {'schema_version': 3, 'layout_version': LAYOUT_VERSION,
            'plugin_version': PLUGIN_VERSION, 'metadata': {'project_name': None,
            'consultant': None, 'investor': None, 'report_type': None, 'design_stage': None,
            'location': None, **(metadata or {})}, 'source_roots': [],
            'sections': []}
        atomic(root / 'project.json', encoded(config))
        p = cls(root)
        try:
            p.put('project', 'project.json', encoded(config), 'system')
            p.put('project-facts', p.path('ai', 'PROJECT_FACTS.json'), encoded(config['metadata']), 'system')
            p.put('decisions', p.path('ai', 'DECISIONS.md'), '# Quyết định dự án\n', 'system')
        finally:
            p.close()
        return {'project': str(root), 'existing': False, 'layout_version': LAYOUT_VERSION, 'missing_metadata':
                [k for k, v in config['metadata'].items() if v is None]}

    def config(self):
        return json.loads((self.root / 'project.json').read_text(encoding='utf-8'))

    def head(self, artifact):
        row = self.db.execute('SELECT r.* FROM heads h JOIN revisions r ON r.id=h.revision '
                              'WHERE h.artifact=?', (artifact,)).fetchone()
        return dict(row) if row else None

    def put(self, artifact, path, data, origin='ai', deps=None, meta=None, actor='host', expected=None, expected_deps=None):
        if origin not in ['ai', 'human', 'system']:
            raise ValueError('Invalid origin')
        target = relative(self.root, path)
        internal = self.path('internal').rstrip('/') + '/'
        if str(path).replace('\\', '/').startswith(internal) and origin != 'system':
            raise ValueError('Reserved internal path')
        if not isinstance(data, bytes): data = data.encode('utf-8')
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.head(artifact)
            if expected is not None and (old or {}).get('id') != expected:
                raise ValueError('Revision changed; merge or refresh first')
            # An untracked human edit must be imported before AI can write again.
            if old and target.exists() and digest(target.read_bytes()) != old['hash'] and origin != 'human':
                raise ValueError('External edit detected; import human revision first')
            collision = self.db.execute('SELECT r.artifact FROM heads h JOIN revisions r '
                'ON r.id=h.revision WHERE r.path=? AND r.artifact<>?', (path, artifact)).fetchone()
            if collision: raise ValueError('Path belongs to another artifact')
            pinned = {}
            for d in deps or []:
                if d == artifact or self.depends_on(d, artifact):
                    raise ValueError('Circular dependency')
                h = self.head(d)
                if not h or self.stale(d): raise ValueError('Missing or stale dependency: ' + d)
                if expected_deps is not None and expected_deps.get(d) != h['id']:
                    raise ValueError('Input revision changed: ' + d)
                pinned[d] = h['id']
            hsh = digest(data)
            if old and old['hash'] == hsh and json.loads(old['deps']) == pinned and json.loads(old['meta']) == (meta or {}) and old['origin'] == origin:
                self.db.rollback(); return {'artifact': artifact, 'revision': old['id'], 'unchanged': True}
            rid = uuid.uuid4().hex
            atomic(self.blob_path(hsh), data)
            # Durable snapshot first; an interrupted head/file update is detected by stale().
            self.db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?)',
                (rid, artifact, hsh, path, origin, actor, json.dumps(pinned),
                 json.dumps(meta or {}, ensure_ascii=False), stamp()))
            self.db.execute('INSERT OR REPLACE INTO heads VALUES(?,?)', (artifact, rid))
            atomic(target, data)
            self.db.commit()
        except BaseException:
            self.db.rollback(); raise
        return {'artifact': artifact, 'revision': rid, 'sha256': hsh, 'path': path}

    def depends_on(self, artifact, ancestor, seen=None):
        seen = set() if seen is None else seen
        if artifact in seen: return False
        seen.add(artifact)
        h = self.head(artifact)
        if not h: return False
        deps = json.loads(h['deps'])
        return ancestor in deps or any(self.depends_on(d, ancestor, seen) for d in deps)

    def stale(self, artifact, seen=None):
        seen = set() if seen is None else set(seen)
        if artifact in seen: return True
        seen.add(artifact)
        h = self.head(artifact)
        if not h: return True
        p = relative(self.root, h['path'])
        if not p.is_file() or digest(p.read_bytes()) != h['hash']: return True
        return any(not self.head(d) or self.head(d)['id'] != rev or self.stale(d, seen)
                   for d, rev in json.loads(h['deps']).items())

    def read(self, artifact):
        h = self.head(artifact)
        if not h: raise ValueError('Unknown artifact')
        return self.blob_path(h['hash']).read_bytes()

    def approve(self, artifact, revision, actor):
        h = self.head(artifact)
        if not actor or not h or h['id'] != revision or self.stale(artifact):
            raise ValueError('Approval requires actor and current fresh revision')
        with self.db:
            self.db.execute('INSERT OR REPLACE INTO approvals VALUES(?,?,?)', (revision, actor, stamp()))
        return {'approved': revision, 'actor': actor}

    def approved(self, artifact):
        h = self.head(artifact)
        return bool(h and not self.stale(artifact) and self.db.execute(
            'SELECT 1 FROM approvals WHERE revision=?', (h['id'],)).fetchone())

    def metadata(self, values):
        if any(not re.fullmatch(r'[a-zA-Z0-9_-]+', key) for key in values):
            raise ValueError('Invalid metadata key')
        cfg = self.config()
        cfg['metadata'].update(values)
        result = self.put('project', 'project.json', encoded(cfg), 'human')
        # Field-level artifacts avoid invalidating technical chapters on consultant-name changes.
        for key, value in values.items():
            if not re.fullmatch(r'[a-zA-Z0-9_-]+', key): raise ValueError('Invalid metadata key')
            self.put('meta:' + key, self.path('ai', 'metadata', key + '.json'), encoded(value), 'human')
        self.put('project-facts', self.path('ai', 'PROJECT_FACTS.json'), encoded(cfg['metadata']), 'human')
        return result

    def select_requirements(self, root, files):
        if not files: raise ValueError('Select at least one requirements file')
        records, deps = [], []
        for name in files:
            source = relative(root, name)
            if source.suffix.lower() != '.md': raise ValueError('Requirements must be Markdown')
            raw = source.read_bytes()
            aid = 'requirement-source:' + digest(name.encode())[:12]
            self.put(aid, self.path('specs', 'sources', name), raw, 'system', meta={'original': name})
            deps.append(aid)
            # Every nonblank paragraph is retained; bullet/heading parsing is not a legal interpretation.
            for i, block in enumerate(re.split(r'\n\s*\n', raw.decode('utf-8-sig'))):
                if block.strip(): records.append({'id': digest((name + ':' + str(i)).encode())[:12],
                    'source': name, 'text': block.strip(), 'applicability': 'pending'})
        self.put('requirements', self.path('specs', 'requirements.json'), encoded(records), 'system', deps)
        return {'requirements': len(records), 'files': files,
                'next': 'Map every requirement to sections or an explicit justified exclusion; verify legal sources.'}

    def define_sections(self, sections, exclusions=None):
        ids = [s['id'] for s in sections]
        if not ids or len(ids) != len(set(ids)): raise ValueError('Unique section IDs required')
        for s in sections:
            if not re.fullmatch(r'[A-Za-z0-9_-]+', s['id']): raise ValueError('Invalid section ID')
            if not s.get('title'): raise ValueError('Section title required')
            for d in s.get('depends_on', []):
                if d not in ids or d == s['id']: raise ValueError('Invalid section dependency')
        done = set()
        while len(done) < len(ids):
            ready = [s['id'] for s in sections if s['id'] not in done and set(s.get('depends_on', [])) <= done]
            if not ready: raise ValueError('Cyclic section graph')
            done.update(ready)
        requirements = json.loads(self.read('requirements'))
        required = {r['id'] for r in requirements}
        mapped = {r for s in sections for r in s.get('requirements', [])}
        exclusions = exclusions or {}
        if any(not isinstance(v, str) or not v.strip() for v in exclusions.values()):
            raise ValueError('Exclusions need reasons')
        if required != mapped | set(exclusions):
            raise ValueError('Coverage incomplete or contains unknown requirement IDs')
        definition = {'sections': sections, 'exclusions': exclusions}
        deps = ['requirements']
        if self.head('domain-request'):
            deps += ['domain:extraction','domain:legal','domain:technical','knowledge-snapshot']
        return self.put('outline', self.path('specs', 'outline.json'), encoded(definition), 'ai', deps)

    def plan(self, mode='incremental', section=None, parallel=2):
        if mode not in ['all', 'section', 'incremental']: raise ValueError('Invalid mode')
        if mode == 'section' and not section: raise ValueError('Section mode requires section ID')
        if not self.approved('outline'): raise ValueError('Approve fresh outline first')
        sections = json.loads(self.read('outline'))['sections']
        byid = {s['id']: s for s in sections}
        if section and section not in byid: raise ValueError('Unknown section')
        wanted = set(byid) if mode == 'all' else {s for s in byid if self.stale('section:' + s)}
        if section:
            wanted = {section}
            changed = True
            while changed:
                more = {s['id'] for s in sections if set(s.get('depends_on', [])) & wanted}
                changed = not more <= wanted; wanted |= more
        done = {s for s in byid if s not in wanted and not self.stale('section:' + s)}
        batches = []
        while wanted:
            ready = [s['id'] for s in sections if s['id'] in wanted and set(s.get('depends_on', [])) <= done]
            if not ready:
                return {'batches': batches, 'blocked': sorted(wanted), 'reason': 'Missing prerequisite sections'}
            batch = ready[:max(1, min(int(parallel), 8))]
            batches.append(batch); done.update(batch); wanted -= set(batch)
        return {'batches': batches, 'blocked': [], 'mode': mode,
                'note': 'Batches are scheduling advice. Host dispatches available workers; workers write distinct sections.'}

    def section(self, sid, text, deps=None, origin='ai', actor='host', expected=None, expected_deps=None):
        if not self.approved('outline'): raise ValueError('Approve fresh outline first')
        spec = next((s for s in json.loads(self.read('outline'))['sections'] if s['id'] == sid), None)
        if not spec: raise ValueError('Unknown section')
        fact_keys = re.findall(r'\{\{fact:([^}]+)\}\}', text)
        dependencies = list(dict.fromkeys(['outline'] + ['section:' + s for s in spec.get('depends_on', [])]
            + ['fact:' + k for k in fact_keys] + (deps or [])))
        return self.put('section:' + sid, self.path('drafts', sid + '.md'), text, origin, dependencies,
                        {'title': spec['title'], 'risk': spec.get('risk', 'normal')}, actor, expected, expected_deps)

    def fact(self, key, record, actor='host'):
        if not re.fullmatch(r'[A-Za-z0-9_-]+', key): raise ValueError('Invalid fact key')
        for field in ['value', 'unit', 'source', 'quote', 'data_type']:
            if field not in record: raise ValueError('Missing fact field: ' + field)
        if not record['source'] or not record['quote']: raise ValueError('Fact needs source and quote')
        if record['data_type'] not in ['PROJECT','REFERENCE','LEGAL','MISSING']:
            raise ValueError('Invalid data_type')
        if record['data_type'] == 'REFERENCE' and not record.get('nguon_du_an'):
            raise ValueError('Reference fact needs project of origin')
        # Each import is a candidate, never a promotion or overwrite of a verified record.
        candidate = {**record, 'status': 'unverified'}
        aid = 'fact:' + key
        old = self.head(aid)
        if old:
            current = json.loads(self.read(aid))
            equal = all(current.get(k) == candidate.get(k) for k in candidate if k != 'status')
            if equal: return {'artifact': aid, 'revision': old['id'], 'unchanged': True}
            candidate = {'status': 'conflict', 'candidates': current.get('candidates', [current]) + [candidate]}
        return self.put(aid, self.path('ai', 'facts', key + '.json'), encoded(candidate), 'ai', actor=actor)

    def resolve_fact(self, key, candidate_index, actor):
        current = json.loads(self.read('fact:' + key))
        candidates = current.get('candidates', [current])
        if not actor or not 0 <= candidate_index < len(candidates): raise ValueError('Invalid approval selection')
        selected = {**candidates[candidate_index], 'status': 'verified'}
        r = self.put('fact:' + key, self.path('ai', 'facts', key + '.json'), encoded(selected), 'human', actor=actor)
        self.approve('fact:' + key, r['revision'], actor)
        return r

    def review(self, sid, findings, reviewer, coverage_checked=False):
        if not reviewer: raise ValueError('Reviewer identity required')
        section = self.head('section:' + sid)
        if section and reviewer == section['actor']:
            raise ValueError('Reviewer must be independent of section author')
        text = self.read('section:' + sid).decode('utf-8')
        for item in findings:
            if item.get('severity') not in ['critical', 'warning'] or not item.get('quote'):
                raise ValueError('Findings need severity and quote')
            if item['quote'] not in text:
                raise ValueError('Finding quote must occur in the reviewed section')
        body = {'reviewer': reviewer, 'coverage_checked': bool(coverage_checked), 'findings': findings}
        return self.put('review:' + sid, self.path('reviews', sid + '.json'), encoded(body), 'ai', ['section:' + sid])

    def assemble(self, final=False):
        if not self.approved('outline'): raise ValueError('Approve fresh outline first')
        sections = json.loads(self.read('outline'))['sections']
        parts, deps, missing = [], ['outline'], []
        for s in sections:
            aid = 'section:' + s['id']
            if self.stale(aid): raise ValueError('Missing/stale section: ' + s['id'])
            text = self.read(aid).decode('utf-8')
            deps.append(aid)
            if final:
                if '{{TODO:' in text or re.search(r'\{\{artifact:', text): missing.append(aid + ': unresolved placeholder')
                if not self.approved(aid): missing.append(aid + ': approval')
                review_id = 'review:' + s['id']
                if self.stale(review_id): missing.append(aid + ': review')
                else:
                    review = json.loads(self.read(review_id))
                    if not review['coverage_checked'] or any(x['severity']=='critical' for x in review['findings']):
                        missing.append(aid + ': coverage/critical findings')
                    deps.append(review_id)
                for d in json.loads(self.head(aid)['deps']):
                    if d.startswith('fact:'):
                        fact = json.loads(self.read(d))
                        if fact.get('status') != 'verified' or not self.approved(d): missing.append(d + ': unverified')
            parts.append(text)
        if final:
            missing += ['metadata:' + k for k,v in self.config()['metadata'].items() if v is None or v == '']
            if self.head('domain-request'):
                from xh_domain import next_tasks
                pending = next_tasks(self).get('tasks', [])
                if not pending or any(t['task'] != 'output' for t in pending):
                    missing.append('domain workflow: unfinished stages')
        if missing: raise ValueError('Final blocked: ' + '; '.join(missing))
        result = self.put('report', self.path('outputs', 'report.md'), '\n\n'.join(parts), 'system', deps,
                        {'stage': 'content-approved' if final else 'draft', 'word_layout_verified': False})
        if final:
            result['post_project_review'] = 'required'
            result['project_complete'] = False
        return result

    def status(self):
        return [{'artifact': r['artifact'], 'revision': r['revision'], 'stale': self.stale(r['artifact']),
                 'approved': self.approved(r['artifact'])} for r in self.db.execute('SELECT * FROM heads')]

    def context(self, artifacts, max_bytes=32000):
        parts, size = [], 0
        for aid in artifacts:
            if self.stale(aid): raise ValueError('Missing/stale context: ' + aid)
            raw = self.read(aid)
            size += len(raw)
            if size > max_bytes: raise ValueError('Context budget exceeded; select smaller artifacts')
            parts.append({'artifact': aid, 'revision': self.head(aid)['id'], 'text': raw.decode('utf-8')})
        return {'items': parts, 'utf8_bytes': size, 'tokens': None}

    def rollback(self, revision, actor):
        r = self.db.execute('SELECT * FROM revisions WHERE id=?', (revision,)).fetchone()
        if not r: raise ValueError('Unknown revision')
        # Pin original dependencies: old text must not be certified against new facts.
        rid = uuid.uuid4().hex
        with self.db:
            self.db.execute('INSERT INTO revisions VALUES(?,?,?,?,?,?,?,?,?)',
                (rid, r['artifact'], r['hash'], r['path'], 'human', actor, r['deps'],
                 json.dumps({'rollback_of': revision}), stamp()))
            atomic(relative(self.root, r['path']), self.blob_path(r['hash']).read_bytes())
            self.db.execute('INSERT OR REPLACE INTO heads VALUES(?,?)', (r['artifact'], rid))
        return {'revision': rid, 'stale': self.stale(r['artifact'])}
