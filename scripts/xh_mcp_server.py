"""Local stdio server. Use an authenticated deployment for remote ChatGPT access."""
import json
import os
from pathlib import Path
from mcp.server.fastmcp import FastMCP
from xh import run
from xh_core import relative
from mcp_project_scraper import scrape_and_save_to_project
from mcp_perplexity_search import search_vietnam_regulations

mcp = FastMCP('xh-tuvan')
mcp.add_tool(scrape_and_save_to_project)
mcp.add_tool(search_vietnam_regulations)

@mcp.tool()
def xh_project(action: str, project_code: str, payload: dict) -> str:
    """Operate a report project. Actions: init,status,metadata,requirements,outline,plan,
    section,fact,resolve-fact,review,approve,assemble,context,register,rollback,execute.
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
        if action == 'requirements':
            allowed = os.getenv('XH_REPORT_LIBRARY')
            if not allowed: raise ValueError('Configure XH_REPORT_LIBRARY')
            payload = {**payload, 'root': allowed}
        return json.dumps(run(action, str(root), payload), ensure_ascii=False)
    except (ValueError, KeyError, OSError) as e:
        return json.dumps({'error': str(e)}, ensure_ascii=False)

if __name__ == '__main__':
    mcp.run(transport='stdio')
