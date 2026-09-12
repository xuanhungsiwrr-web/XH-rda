"""Local stdio server. Use an authenticated deployment for remote ChatGPT access."""
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from xh import run
from xh_core import relative

mcp = FastMCP('xh-tuvan')

@mcp.tool()
def xh_project(action: str, project_code: str, payload: dict) -> str:
    """Operate a report project. Actions: init,status,metadata,requirements,outline,plan,
    section,fact,resolve-fact,review,approve,assemble,context,register,rollback,
    start,domain-next,domain-accept,post-review,complete,migrate-domain,layout,
    workspace-preflight,workspace-dry-run,workspace-migrate,workspace-verify,
    workspace-rollback,workspace-resume,render,release,delivery-status,import-feedback.
    Approve/resolve-fact only after actual user approval; payload actor identifies the user.
    Returns revision/paths rather than large source documents. Read the workflow reference.
    """
    base = os.getenv('XH_PROJECTS_ROOT')
    if not base: return json.dumps({'error': 'Configure XH_PROJECTS_ROOT'})
    if action in ['conductor', 'library']:
        return json.dumps({'error': 'Use CLI for host/library discovery'})
    try:
        root = relative(base, project_code)
        if action == 'export':
            payload = {**payload, 'destination': str(relative(root, payload['destination']))}
        if action in ['requirements', 'start']:
            allowed = os.getenv('XH_REPORT_LIBRARY')
            if action == 'requirements':
                if not allowed: raise ValueError('Configure XH_REPORT_LIBRARY')
                payload = {**payload, 'root': allowed}
            else:
                payload = {**payload, 'library_root': allowed}
        return json.dumps(run(action, str(root), payload), ensure_ascii=False)
    except (ValueError, KeyError, OSError) as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)

@mcp.tool()
def xh_learning(action: str, payload: dict) -> str:
    """Shared domain learning: candidate,validate,reject,deprecate,snapshot,change-request,evaluate.
    Approval and release are operator-only CLI actions, never automatic model tools.
    """
    from xh_learning import learning_action
    try:
        if action not in ['candidate','validate','reject','snapshot','change-request','evaluate']:
            raise ValueError('Operator approval required via learning_admin.py')
        return json.dumps(learning_action(action, payload), ensure_ascii=False)
    except (ValueError, KeyError, OSError) as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)

if __name__ == '__main__':
    mcp.run(transport='stdio')
