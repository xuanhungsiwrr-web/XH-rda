"""CLI shared by hosts and the MCP bridge. Payload is a JSON file, not shell text."""
import argparse
import json
from pathlib import Path
import sys
from xh_core import Project, PLUGIN, library, relative
from xh_router import conductor, execute
from xh_artifacts import ingest, retrieve, attachment, edit_guard, render, export_project, templates

def run(action, root, data):
    if action == 'init': return Project.init(root, data.get('metadata'))
    if action == 'conductor': return conductor(**data)
    if action == 'library': return library(data['root'], data.get('query', ''))
    p = Project(root)
    try:
        if action == 'status': return p.status()
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
        if action == 'render': return render(p, **data)
        if action == 'templates': return templates(p)
        if action == 'export': return export_project(p, **data)
        if action == 'register':
            # File must already be within project, e.g. imported via user's Drive connector.
            file = relative(p.root, data.pop('path'))
            return p.put(path=file.relative_to(p.root).as_posix(), data=file.read_bytes(), **data)
        if action == 'execute':
            registry = json.loads((PLUGIN / 'config/providers.json').read_text(encoding='utf-8'))
            local = PLUGIN / 'config/providers.local.json'
            if local.exists(): registry = json.loads(local.read_text(encoding='utf-8'))
            return execute(p, registry, **data)
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
