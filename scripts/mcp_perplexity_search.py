import os
import json
from mcp.server.fastmcp import FastMCP
from xh_core import Project, relative
from xh_web import legal_search
mcp = FastMCP('PerplexityLegalSearch')

@mcp.tool()
def search_vietnam_regulations(query: str, project_code: str, recency: str | None = None) -> str:
    """Paid legal discovery. No date filter by default. Saves full answer/citations to research/.
    Uses a direct Perplexity call, outside the generic router budget; host must account for usage.
    Verify original documents before approving facts or references.
    """
    base = os.getenv('XH_PROJECTS_ROOT')
    if not base: return 'Configure XH_PROJECTS_ROOT'
    p = Project(relative(base, project_code))
    try: return json.dumps(legal_search(p,query,recency),ensure_ascii=False)
    finally: p.close()

if __name__ == '__main__': mcp.run()
