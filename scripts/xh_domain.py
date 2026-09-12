"""Construction workflow and opaque capability packets; no execution-provider policy."""
import difflib
import json
import os
import re
from pathlib import Path
from xh_core import Project, PLUGIN, encoded, digest, fold

ROLES = {'MASTER', 'TECHNICAL_SPECIALIST', 'EXTRACTOR', 'REVIEWER', 'RESEARCHER'}
REPORTS = {
    'NCKT': ['Nội dung Báo cáo Nghiên cứu Khả thi và thuyết minh TKCS.md'],
    'DXCTDT': ['Nội dung Chủ trương Đầu tư và Thiết kế Sơ bộ Dự án.md'],
    'KTKT': ['Nội dung Hồ sơ Báo cáo Kinh tế - Kỹ thuật Đầu tư Xây dựng.md'],
}
HYDRAULIC = {
    'NCKT': 'TCVN_Nội dung thuyết minh Báo cáo nghiên cứu khả thi dự án thủy lợi.md',
    'DXCTDT': 'TCVN_Lập Báo cáo Đề xuất Chủ trương Đầu tư Thủy lợi.md',
    'KTKT': 'TCVN_Lập Thuyết minh Báo cáo Kinh tế - Kỹ thuật Xây dựng.md',
}

def report_type(request):
    q = re.sub(r'[^a-z0-9 ]', '', fold(request))
    choices = {'NCKT': ['nckt', 'nghien cuu kha thi'],
               'DXCTDT': ['dxctdt', 'de xuat chu truong dau tu', 'chu truong dau tu'],
               'KTKT': ['ktkt', 'kinh te ky thuat']}
    found = [key for key, terms in choices.items() if any(t in q for t in terms)]
    if len(found) != 1: raise ValueError('Cần xác định một loại báo cáo: NCKT, ĐXCTĐT hoặc KT-KT')
    return found[0]

def migrate(p):
    """Expand current facts into .ai; immutable old revisions remain available for rollback."""
    cfg = p.config()
    changed = cfg.get('schema_version', 1) < 2
    if changed:
        cfg.pop('budget', None); cfg.pop('execution', None)
        cfg['schema_version'] = 2
        p.put('project', 'project.json', encoded(cfg), 'system')
    if not p.head('project-facts'):
        p.put('project-facts', p.path('ai','PROJECT_FACTS.json'), encoded(cfg['metadata']), 'system')
    if not p.head('decisions'):
        p.put('decisions', p.path('ai','DECISIONS.md'), '# Quyết định dự án\n', 'system')
    for row in p.status():
        aid = row['artifact']
        if aid.startswith(('fact:', 'meta:')):
            h = p.head(aid)
            folder = 'facts' if aid.startswith('fact:') else 'metadata'
            path = p.path('ai', folder, aid.split(':', 1)[1] + '.json')
            if h['path'] != path:
                if p.stale(aid): raise ValueError('Import external edits before migration: ' + aid)
                p.put(aid, path, p.read(aid), 'system', list(json.loads(h['deps'])),
                      {'migrated_from': h['path']})
                changed = True
    return {'migrated': changed, 'schema_version': 2,
            'note': 'Old snapshots retained; migrated facts need reapproval. Check stale descendants.'}

def start(root, request, metadata=None, library_root=None, sector=None):
    kind = report_type(request)
    Project.init(root, {**(metadata or {}), 'report_type': kind})
    p = Project(root)
    try:
        migrate(p)
        previous = json.loads(p.read('domain-request')) if p.head('domain-request') else None
        definition = {'request': request, 'report_type': kind, 'sector': sector}
        if previous and previous != definition:
            raise ValueError('Existing workflow differs; use a separate project/report workspace')
        if not previous:
            p.metadata({**(metadata or {}), 'report_type': kind})
            files = REPORTS[kind] + ([HYDRAULIC[kind]] if sector == 'thuy-loi' else [])
            p.select_requirements(library_root or os.getenv('XH_REPORT_LIBRARY') or PLUGIN/'packs/report-library', files)
            p.put('domain-request', p.path('ai','REQUEST.json'), encoded(definition), 'human')
        from xh_learning import Learning
        with Learning() as kb:
            snapshot = kb.snapshot()
        # A run pins approved knowledge; resume cannot silently introduce new rules.
        if not p.head('knowledge-snapshot'):
            p.put('knowledge-snapshot', p.path('ai','KNOWLEDGE_SNAPSHOT.json'), encoded(snapshot), 'system')
        return next_tasks(p)
    finally:
        p.close()

def packet(p, name, role, objective, inputs, output):
    refs = {aid: p.head(aid)['id'] for aid in inputs}
    body = {'contract': 'xh-tuvan.capability.v1', 'task': name, 'capability': role,
            'objective': objective, 'input_revisions': refs, 'output_artifact': output}
    body['task_id'] = digest(encoded(body))[:24]
    return body

def next_tasks(p):
    if not p.head('domain-request'): raise ValueError('Call start with high-level request first')
    base = ['domain-request', 'requirements', 'knowledge-snapshot', 'project-facts']
    stages = [
        ('extraction', 'EXTRACTOR', 'Trích nguồn thành facts có vị trí trích dẫn; ghi dữ liệu thiếu, xung đột; không suy đoán.'),
        ('legal', 'RESEARCHER', 'Đối chiếu văn bản gốc, hiệu lực, sửa đổi và phạm vi áp dụng; kết quả tìm kiếm chưa là căn cứ đã xác minh.'),
        ('technical', 'TECHNICAL_SPECIALIST', 'Phân biệt số liệu đã xác minh, giả định, tính toán và thông tin còn thiếu; chỉ rõ đầu vào từng tính toán.'),
    ]
    tasks = []
    upstream = list(base)
    # Source revisions invalidate extraction and every downstream domain stage.
    upstream += [r['artifact'] for r in p.status() if r['artifact'].startswith(('source:', 'web:', 'extracted:'))]
    for name, role, objective in stages:
        aid = 'domain:' + name
        if any(p.stale(a) for a in upstream):
            return {'state': 'blocked', 'reason': 'Import changed input artifacts', 'tasks': []}
        if p.stale(aid) or json.loads(p.head(aid)['deps']) != {a:p.head(a)['id'] for a in upstream}:
            tasks.append(packet(p, name, role, objective, upstream, aid))
            break
        upstream.append(aid)
    if not tasks:
        if not p.approved('outline'):
            tasks = [packet(p, 'outline', 'MASTER',
                'Tự xây outline theo toàn bộ requirement IDs, giải trình ngoại lệ và phụ thuộc; dùng outline rồi xin duyệt. Không hỏi người dùng phân chương cho model.',
                upstream, 'outline')]
        else:
            for batch in p.plan()['batches'][:1]:
                for sid in batch:
                    spec = next(s for s in json.loads(p.read('outline'))['sections'] if s['id'] == sid)
                    inputs = upstream + ['outline'] + ['section:'+x for x in spec.get('depends_on', [])]
                    tasks.append(packet(p, 'draft:'+sid, 'MASTER',
                        'Viết phần '+spec['title']+'; giữ nguồn, TODO, fact placeholders, liên kết artifact và phạm vi đề mục.', inputs, 'section:'+sid))
            if not tasks:
                for s in json.loads(p.read('outline'))['sections']:
                    sid = s['id']
                    if p.stale('review:'+sid):
                        tasks.append(packet(p, 'qa:'+sid, 'REVIEWER',
                            'Kiểm coverage, dữ liệu/giả định, căn cứ pháp lý, tính toán và nhất quán; findings phải có câu trích.',
                            ['outline','section:'+sid], 'review:'+sid))
            if not tasks:
                tasks = [packet(p, 'output', 'MASTER',
                    'Chốt các phê duyệt còn thiếu; assemble final, render Word, kiểm layout; post-review rồi complete. Không tự xác nhận phê duyệt của người dùng.',
                    ['outline'] + ['section:'+s['id'] for s in json.loads(p.read('outline'))['sections']], 'report')]
    state = {'state': 'awaiting_capability', 'tasks': tasks,
             'resolution': 'Global Control resolves capability; domain never selects models or retries providers.'}
    p.put('domain-state', p.path('ai','STATE.md'), '# Trạng thái workflow\n\n```json\n'+json.dumps(state, ensure_ascii=False, indent=2)+'\n```\n', 'system')
    return state

def accept(p, task_id, content, actor, findings=None, coverage_checked=False):
    tasks = next_tasks(p)['tasks']
    t = next((t for t in tasks if t['task_id'] == task_id), None)
    if not t: raise ValueError('Task expired or inputs changed; refresh domain-next')
    if not actor or not isinstance(content, str) or not content.strip(): raise ValueError('Content and actor required')
    name, aid = t['task'], t['output_artifact']
    deps = list(t['input_revisions'])
    if name in ['outline', 'output']:
        raise ValueError('Use structured outline/approve or assemble/render/post-review/complete actions')
    if name.startswith('draft:'):
        return p.section(name.split(':')[1], content, deps=deps, actor=actor,
                         expected_deps={**t['input_revisions'], **{a:p.head(a)['id'] for a in re.findall(r'\{\{(fact:[^}]+)\}\}', content)}})
    if name.startswith('qa:'):
        return p.review(name.split(':')[1], findings or [], actor, coverage_checked)
    return p.put(aid, p.path('ai','stages',name+'.md'), content, 'ai', deps,
                 {'capability':t['capability'], 'task_id':task_id, 'verification':'candidate'}, actor,
                 expected_deps=t['input_revisions'])

def post_review(p, feedback, before_revision, lessons=None):
    """Raw review stays in project. Explicit reusable abstractions enter shared candidates."""
    if p.stale('report'): raise ValueError('Assemble current report before post-review')
    if not isinstance(feedback, str) or not feedback.strip(): raise ValueError('Feedback required, including explicit no-change feedback')
    before = p.db.execute('SELECT * FROM revisions WHERE id=? AND artifact=?', (before_revision, 'report')).fetchone()
    if not before: raise ValueError('before_revision must identify an actual report revision')
    old = p.blob_path(before['hash']).read_text(encoding='utf-8')
    new = p.read('report').decode('utf-8')
    diff = ''.join(difflib.unified_diff(old.splitlines(True), new.splitlines(True), fromfile='before', tofile='after'))
    p.put('review-diff', p.path('edit_analysis','REVIEW_DIFF.md'), diff or 'Không có thay đổi văn bản.\n', 'system', ['report'])
    from xh_learning import Learning
    candidates, global_handoffs = [], []
    with Learning() as kb:
        for lesson in lessons or []:
            scope = lesson.get('scope')
            if scope == 'global':
                global_handoffs.append({'destination':'GLOBAL_CONTROL', 'payload':lesson})
            elif scope == 'project':
                key = digest(encoded(lesson))[:16]
                p.put('project-lesson:'+key, p.path('learning_candidates','project-'+key+'.json'), encoded(lesson), 'human')
            else:
                candidates.append(kb.candidate(**lesson))
        records = [{'id':r['id'], 'status':r['status']} for r in candidates]
    previous_ids = []
    if p.head('post-review'):
        previous_ids = json.loads(p.read('post-review').decode().split('\n\n',1)[1])['candidate_ids']
    candidate_ids = list(dict.fromkeys(previous_ids + [r['id'] for r in records]))
    body = {'feedback':feedback, 'before_revision':before_revision, 'after_revision':p.head('report')['id'],
            'candidate_ids':candidate_ids, 'global_handoff_count':len(global_handoffs),
            'no_reusable_lesson':not records}
    p.put('post-review', p.path('ai','POSTMORTEM.md'), '# Post-Project Review\n\n'+json.dumps(body, ensure_ascii=False, indent=2),
          'human', ['report','review-diff'])
    return {**body, 'global_handoffs':global_handoffs, 'next':'Validate candidates; explicit approval is required before promotion.'}

def complete(p):
    if p.stale('report') or json.loads(p.head('report')['meta']).get('stage') != 'content-approved':
        raise ValueError('Approved final content required')
    if p.stale('post-review'): raise ValueError('Post-Project Review required for this report revision')
    body = json.loads(p.read('post-review').decode().split('\n\n', 1)[1])
    from xh_learning import Learning
    with Learning() as kb:
        pending = [lid for lid in body['candidate_ids'] if kb.get(lid)['status'] not in ['approved','rejected','deprecated']]
    if pending: raise ValueError('Learning validation/approval pending: '+', '.join(pending))
    result = p.put('completion', p.path('ai','COMPLETION.json'), encoded({'report_revision':p.head('report')['id'],
        'knowledge_snapshot':json.loads(p.read('knowledge-snapshot')) if p.head('knowledge-snapshot') else None}),
        'system', ['report','post-review'])
    return {**result, 'project_complete':True, 'word_layout_verified':False,
            'note':'Content workflow complete; Word delivery still requires visual layout verification.'}
