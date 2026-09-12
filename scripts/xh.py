"""CLI shared by hosts and the MCP bridge. Payload is a JSON file, not shell text."""
import argparse
import json
from pathlib import Path
import sys
from xh_core import Project, PLUGIN, library, relative
from xh_artifacts import ingest, retrieve, attachment, edit_guard, render, export_project, templates
from xh_delivery import delivery_status, import_feedback
from xh_layout import LAYOUT_VERSION, V3_PATHS

def run(action, root, data):
    if action in ['workspace-preflight','workspace-dry-run','workspace-migrate','workspace-verify','workspace-rollback','workspace-resume']:
        from xh_migration import preflight, apply, verify, rollback
        actions = {'workspace-preflight':preflight, 'workspace-dry-run':preflight,
                   'workspace-migrate':apply, 'workspace-resume':apply, 'workspace-verify':verify,
                   'workspace-rollback':lambda value: rollback(value, data.get('migration_id'))}
        return actions[action](root)
    if action == 'layout': return {'layout_version':LAYOUT_VERSION, 'paths':V3_PATHS}
    if action == 'init': return Project.init(root, data.get('metadata'))
    if action == 'start':
        from xh_domain import start
        return start(root, **data)
    if action == 'library': return library(data['root'], data.get('query', ''))
    p = Project(root)
    try:
        if action == 'status': return p.status()
        if action in ['domain-next', 'domain-accept', 'post-review', 'complete', 'migrate-domain']:
            from xh_domain import next_tasks, accept, post_review, complete, migrate
            return {'domain-next': next_tasks, 'domain-accept': accept, 'post-review': post_review,
                    'complete': complete, 'migrate-domain': migrate}[action](p, **data)
        if action == 'metadata': return p.metadata(data)
        if action == 'requirements': return p.select_requirements(**data)
        if action == 'outline': return p.define_sections(**data)
        if action == 'approve': return p.approve(**data)
        if action == 'plan': return p.plan(**data)
        if action == 'section': return p.section(**data)
        if action == 'fact': return p.fact(**data)
        if action == 'resolve-fact': return p.resolve_fact(**data)
        if action == 'review': return p.review(**data)
        if action == 'assemble': return p.assemble(**data)
        if action == 'context': return p.context(**data)
        if action == 'rollback': return p.rollback(**data)
        if action == 'ingest': return ingest(p, **data)
        if action == 'retrieve': return retrieve(p, **data)
        if action == 'attachment': return attachment(p, **data)
        if action == 'edit-guard': return edit_guard(**data)
        if action in ['render','release']:
            if action == 'release': data = {**data, 'final':True}
            return render(p, **data)
        if action == 'delivery-status': return delivery_status(p, **data)
        if action == 'import-feedback': return import_feedback(p, **data)
        if action == 'templates': return templates(p)
        if action == 'export': return export_project(p, **data)
        if action == 'register':
            # File must already be within project, e.g. imported via user's Drive connector.
            file = relative(p.root, data.pop('path'))
            return p.put(path=file.relative_to(p.root).as_posix(), data=file.read_bytes(), **data)
        raise ValueError('Unknown action: ' + action)
    finally:
        p.close()

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('action')
    ap.add_argument('--project', required=True)
    ap.add_argument('--data', help='UTF-8 JSON payload file')
    a = ap.parse_args()
    try:
        result = run(a.action, a.project, json.loads(Path(a.data).read_text(encoding='utf-8-sig')) if a.data else {})
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, KeyError, OSError) as e:
        print(json.dumps({'error': str(e)}, ensure_ascii=False), file=sys.stderr)
        sys.exit(2)
