import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import yaml

ROOT=Path(__file__).resolve().parents[1]

class LegacyContracts(unittest.TestCase):
    def test_notebook_import_preserves_conflict(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            facts=root/'facts.yaml'; answer=root/'answer.md'
            original={'h':{'value':2,'status':'conflict','candidates':[1,2]}}
            facts.write_text(yaml.safe_dump(original),encoding='utf-8')
            answer.write_text('| khoa | value | unit | source | quote |\n|---|---|---|---|---|\n| h | 3 | m | p1 | 3m |',encoding='utf-8')
            proc=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/doc-ket-qua-notebooklm.py'),
                '--ket-qua',str(answer),'--facts',str(facts),'--ra',str(facts)],capture_output=True)
            self.assertEqual(proc.returncode,0,proc.stderr)
            self.assertEqual(yaml.safe_load(facts.read_text()),original)

    def test_renderer_missing_ordered_section_fails(self):
        import docx
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); docx.Document().save(root/'template.docx')
            (root/'A.md').write_text('# A\nContent',encoding='utf-8')
            proc=subprocess.run([sys.executable,'-X','utf8',str(ROOT/'scripts/render_report.py'),
                '--khuon',str(root/'template.docx'),'--noidung',str(root),'--thu-tu','A.md,missing.md',
                '--ra',str(root/'out.docx')],capture_output=True)
            self.assertNotEqual(proc.returncode,0)
            self.assertFalse((root/'out.docx').exists())

    def test_library_snapshot_keeps_nine_sources(self):
        sources=list((ROOT/'packs/report-library').glob('*.md'))
        self.assertEqual(len(sources),9)

if __name__=='__main__': unittest.main()
