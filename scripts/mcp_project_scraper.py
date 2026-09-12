import os
import json
from mcp.server.fastmcp import FastMCP
from xh_core import Project, relative
from xh_web import scrape
mcp = FastMCP('ProjectWebScraper')

@mcp.tool()
def scrape_and_save_to_project(url: str, project_code: str, refresh: bool = False) -> str:
    """Capture a public HTML page into research/, return only artifact ID and path.
    Project must already exist under XH_PROJECTS_ROOT. Does not write report drafts.
    """
    base = os.getenv('XH_PROJECTS_ROOT')
    if not base: return 'Configure XH_PROJECTS_ROOT'
    p = Project(relative(base, project_code))
    try: return json.dumps(scrape(p,url,refresh),ensure_ascii=False)
    finally: p.close()

if __name__ == '__main__': mcp.run()
