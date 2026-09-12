import asyncio
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

class MCPTests(unittest.TestCase):
    def test_real_stdio_tools_and_project(self):
        async def check(root):
            server=Path(__file__).resolve().parents[1]/'scripts/xh_mcp_server.py'
            params=StdioServerParameters(command=sys.executable,args=[str(server)],
                env={**os.environ,'XH_PROJECTS_ROOT':root,'PYTHONUTF8':'1'})
            async with stdio_client(params) as (read,write):
                async with ClientSession(read,write) as session:
                    await session.initialize()
                    tools=await session.list_tools()
                    names={t.name for t in tools.tools}
                    self.assertTrue({'xh_project','scrape_and_save_to_project','search_vietnam_regulations'}<=names)
                    result=await session.call_tool('xh_project',{'action':'init','project_code':'demo',
                        'payload':{'metadata':{'project_name':'MCP fixture'}}})
                    self.assertFalse(result.isError)
                    parsed=json.loads(result.content[0].text)
                    self.assertFalse(parsed['existing'])
                    status=await session.call_tool('xh_project',{'action':'status','project_code':'demo','payload':{}})
                    self.assertIn('project',status.content[0].text)
        with tempfile.TemporaryDirectory() as root: asyncio.run(check(root))
