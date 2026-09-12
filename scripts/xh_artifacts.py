"""Source index, selective retrieval, attachments, and one-pass report rendering."""
import json
import os
from pathlib import Path
import re
import subprocess
import sys
import zipfile
from collections import Counter
from xh_core import PLUGIN, atomic, digest, encoded, fold, relative, stamp
from xh_delivery import deliver_bytes

def ingest(project, path, source_id=None, source_url=None, source_kind='PROJECT'):
    file = relative(project.root, path)
    if source_kind not in ['PROJECT','REFERENCE','LEGAL']: raise ValueError('Invalid source kind')
    if not file.is_file(): raise ValueError('Copy/download source inside project first')
    sid = source_id or digest(path.encode())[:20]
    if not re.fullmatch(r'[A-Za-z0-9_-]+', sid): raise ValueError('Invalid source ID')
    aid = 'source:' + sid
    result = project.put(aid, path, file.read_bytes(), 'human',
        meta={'source_id':sid, 'url':source_url, 'kind':source_kind})
    return {**result, 'next':'Convert to Markdown with source hash dependency; preserve page/cell references'}

def retrieve(project, query, limit=5, max_chars=12000):
    if not 1 <= limit <= 20 or not 1 <= max_chars <= 64000: raise ValueError('Invalid retrieval budget')
    terms = set(re.findall(r'\w+', fold(query)))
    candidates = []
    for h in project.status():
        if h['stale'] or not h['artifact'].startswith(('source:', 'web:', 'extracted:', 'legal-search:')): continue
        record = project.head(h['artifact'])
        if not record['path'].endswith(('.md','.txt','.json')): continue
        text = project.read(h['artifact']).decode('utf-8')
        for index, block in enumerate(re.split(r'\n\s*\n', text)):
            score = len(terms & set(re.findall(r'\w+', fold(block))))
            if score: candidates.append({'artifact':h['artifact'], 'revision':h['revision'],
                'block':index, 'score':score, 'text':block, 'path':record['path']})
    candidates.sort(key=lambda c:-c['score'])
    selected, used = [], 0
    for c in candidates:
        if len(selected) == limit: break
        if used + len(c['text']) > max_chars: continue
        selected.append(c); used += len(c['text'])
    return {'matches':selected, 'chars':used, 'tokens':None,
        'note':'Whole matching paragraphs; no silent truncation. Broaden query/read source if coverage is inadequate.'}

def edit_guard(before, after):
    # Deterministic guard is necessary but not sufficient for semantic equivalence.
    patterns = [r'\{\{[^}]+\}\}', r'\d+(?:[.,]\d+)*', r'https?://[^\s)]+',
                r'(?m)^#{1,6} .+$', r'(?m)^\|.*\|$', r'```[\s\S]*?```']
    violations = []
    for pattern in patterns:
        if Counter(re.findall(pattern,before)) != Counter(re.findall(pattern,after)):
            violations.append(pattern)
    return {'protected_content_preserved':not violations, 'violations':violations,
            'semantic_review_required':True}

def attachment(project, name, file, summary, deps=None, actor='user'):
    if not re.fullmatch(r'[A-Za-z0-9_-]+',name): raise ValueError('Invalid attachment ID')
    path = relative(project.root,file)
    source = project.put('calculation:' + name, file, path.read_bytes(), 'human', deps, actor=actor)
    summary_path = project.path('evidence', 'calculation-summaries', name + '-summary.md')
    result = project.put('attachment:' + name, summary_path, summary,
        'human', ['calculation:' + name], {'original_path':file}, actor)
    return {**result, 'original':source,
            'next':'Review formulas/units/source cells; approve facts explicitly. Insert summary MD, not a binary DOCX merge.'}

def render(project, template, template_map, final=False, section=None, release_id=None, output_name=None, simulate_failure_after_output=False):
    import yaml
    template_path = relative(project.root, template)
    contract_path = relative(project.root, template_map)
    project.put('template',template,template_path.read_bytes(),'human')
    project.put('template-map',template_map,contract_path.read_bytes(),'human')
    if section:
        aid = 'section:' + section
        if project.stale(aid): raise ValueError('Section is stale')
        content = project.read(aid)
        report_deps = [aid]
        if final: raise ValueError('Section render is a preview, not final report')
    else:
        project.assemble(final)
        content = project.read('report'); report_deps = ['report']
    facts = {}
    for key in set(re.findall(r'\{\{fact:([^}]+)\}\}',content.decode())):
        if project.head('fact:' + key): facts[key] = json.loads(project.read('fact:' + key))
    metadata = project.config()['metadata']
    info = {str(k).upper(): v if v is not None else '{{TODO: '+k+'}}' for k,v in metadata.items()}
    # Compatibility placeholder aliases belong to the presentation adapter.
    for key, target in {'project_name':'TEN_DU_AN','consultant':'DON_VI_TU_VAN','investor':'CHU_DAU_TU',
        'report_type':'LOAI_BAO_CAO','design_stage':'GIAI_DOAN','location':'DIA_DIEM'}.items():
        info[target] = info.get(key.upper(),'{{TODO: '+key+'}}')
    build = project.layout.at(project.root, 'render')
    build.mkdir(exist_ok=True)
    atomic(build/'content.md', content)
    atomic(build/'facts.yaml',yaml.safe_dump(facts,allow_unicode=True).encode())
    atomic(build/'info.yaml',yaml.safe_dump(info,allow_unicode=True).encode())
    out = build/'report.docx'
    args = [sys.executable,str(PLUGIN/'scripts/render_report.py'),'--khuon',str(template_path),
        '--template-map',str(contract_path),'--noidung',str(build/'content.md'),
        '--facts',str(build/'facts.yaml'),'--info',str(build/'info.yaml'),
        '--hinh',str(project.root),'--ra',str(out)]
    proc = subprocess.run(args,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=120,
                          env={**os.environ,'PYTHONUTF8':'1'})
    if proc.returncode or not out.exists():
        raise ValueError('Render rejected: '+proc.stdout[-2000:]+proc.stderr[-1000:])
    if final:
        if not release_id: raise ValueError('Final render requires release_id')
        return deliver_bytes(project, release_id, out.read_bytes(), output_name,
                             simulate_failure_after_output=simulate_failure_after_output)
    suffix = '-'+section if section else ''
    preview_name = 'report'+suffix+'.docx'
    result = project.put('word-preview'+suffix, project.path('render','previews',preview_name),
                         out.read_bytes(),'system', report_deps+['template','template-map','project'],
                         {'stage':'preview-only','rendered_at':stamp()})
    return {**result,'next':'Preview only; final release requires release_id and creates an immutable pair'}

def export_project(project, destination):
    """Export snapshots + owned project files, not arbitrary credential/config files."""
    out = Path(destination)
    if out.exists(): raise ValueError('Export destination exists')
    paths = {'project.json'}
    for r in project.db.execute('SELECT path,hash FROM revisions'):
        paths.add(r['path']); paths.add(project.path('artifacts', r['hash']))
    # Freeze DB via SQLite backup; do not zip a live SQLite database.
    import sqlite3, tempfile
    with tempfile.TemporaryDirectory() as temp:
        dbpath = Path(temp)/'state.sqlite'
        db = sqlite3.connect(dbpath)
        project.db.backup(db); db.close()
        out.parent.mkdir(parents=True,exist_ok=True)
        with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
            for name in sorted(paths):
                p = relative(project.root,name)
                if p.is_file(): z.write(p,name)
            z.write(dbpath,project.path('state_db'))
    return {'path':str(out),'note':'Contains registered artifacts and revisions only. Register input files before export.'}


def templates(project):
    """Discover per-template manifests without guessing organization from a filename."""
    metadata = project.config()['metadata']
    candidates = []
    for file in sorted(project.layout.at(project.root,'templates').glob('*.template.json')):
        try:
            manifest = json.loads(file.read_text(encoding='utf-8'))
            target = relative(project.root, manifest['file'])
            contract = relative(project.root, manifest['contract'])
            if not target.is_file() or not contract.is_file(): raise ValueError('Missing template/contract')
            conditions = manifest.get('matches',{})
            mismatch = [k for k,v in conditions.items() if metadata.get(k) is not None and metadata.get(k) not in v]
            unknown = [k for k in conditions if metadata.get(k) is None]
            candidates.append({'id':manifest['id'],'file':manifest['file'],'contract':manifest['contract'],
                'eligible':not mismatch,'unresolved':unknown,'mismatch':mismatch,
                'score':len(conditions)-len(mismatch)-len(unknown),'sha256':digest(target.read_bytes())})
        except (ValueError,KeyError,TypeError) as e:
            candidates.append({'manifest':file.name,'eligible':False,'error':str(e)})
    return sorted(candidates,key=lambda c:(not c['eligible'],-c.get('score',0)))
