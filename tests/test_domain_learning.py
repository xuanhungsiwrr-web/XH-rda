import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from xh_core import Project, encoded
from xh_domain import start, next_tasks, accept, post_review, complete, migrate, report_type
from xh_learning import Learning
from xh_evolution import release

class DomainTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)/'project'
        self.kb=Path(self.tmp.name)/'shared'
        self.env=patch.dict(os.environ,{'XH_TUVAN_KNOWLEDGE_ROOT':str(self.kb)}); self.env.start()
    def tearDown(self): self.env.stop(); self.tmp.cleanup()

    def start(self):
        return start(self.root,'Lập Báo cáo NCKT dự án X',metadata={k:'fixture' for k in
            ['project_name','consultant','investor','design_stage','location']})

    def stages(self,p):
        for name in ['extraction','legal','technical']:
            task=next_tasks(p)['tasks'][0]; self.assertEqual(task['task'],name)
            accept(p,task['task_id'],'Evidence summary: missing inputs explicitly identified.','worker-'+name)

    def outline(self,p):
        ids=[r['id'] for r in json.loads(p.read('requirements'))]
        p.define_sections([{'id':'A','title':'A','requirements':ids},
                           {'id':'B','title':'B','requirements':[],'depends_on':['A']}])
        p.approve('outline',p.head('outline')['id'],'user')

    def test_types_and_minimum_library(self):
        for request,kind in [('Lập ĐXCTĐT dự án Y','DXCTDT'),('Lập KT-KT dự án Z','KTKT'),('Lập NCKT X','NCKT')]:
            self.assertEqual(report_type(request),kind)
            root=self.root/kind
            state=start(root,request)
            self.assertEqual(state['tasks'][0]['capability'],'EXTRACTOR')
            p=Project(root)
            try: self.assertGreater(len(json.loads(p.read('requirements'))),5)
            finally:p.close()

    def test_same_workflow_for_any_master_and_stale_result(self):
        self.start(); p=Project(self.root)
        try:
            task=next_tasks(p)['tasks'][0]
            # Resolver identity never enters domain graph or packet.
            resolved=[{'worker':host,'packet':task} for host in ['host-one','host-two']]
            self.assertEqual(resolved[0]['packet'],resolved[1]['packet'])
            p.put('source:new','sources/new.md','New source','human')
            with self.assertRaises(ValueError):accept(p,task['task_id'],'Old input result','worker')
            self.stages(p); self.outline(p)
            t=next_tasks(p)['tasks'][0]
            self.assertEqual(t['task'],'draft:A')
            accept(p,t['task_id'],'# A\nContent','writer')
            self.assertEqual(next_tasks(p)['tasks'][0]['task'],'draft:B')
        finally:p.close()

    def test_postreview_required_and_changed_report_invalidates(self):
        self.start(); p=Project(self.root)
        try:
            self.stages(p); self.outline(p)
            for sid in ['A','B']:
                t=next_tasks(p)['tasks'][0]; accept(p,t['task_id'],'# '+sid+'\nReviewed content','writer')
                p.review(sid,[],'independent',True); p.approve('section:'+sid,p.head('section:'+sid)['id'],'user')
            p.assemble(True)
            with self.assertRaises(ValueError):complete(p)
            post_review(p,'Đã kiểm, không có lỗi cần khái quát.',p.head('report')['id'])
            self.assertTrue(complete(p)['project_complete'])
            candidate=dict(title='PPR source issue',rule='Trace facts to source',
                evidence=[{'reference':'sanitized-fixture','quote':'Missing source'}],author='writer',
                cases=[{'input':{'facts':[{}]},'expected_findings':['missing_source'],'explanation':'Source guard'}])
            outcome=post_review(p,'Đề xuất bài học sau hậu kiểm.',p.head('report')['id'],[candidate])
            lid=outcome['candidate_ids'][0]
            with self.assertRaises(ValueError):complete(p)
            post_review(p,'Bổ sung feedback, không xóa bài học đang chờ.',p.head('report')['id'],[])
            with self.assertRaises(ValueError):complete(p)
            with Learning(self.kb) as kb:
                row=kb.validate(lid,'reviewer',True,True,True,'Synthetic review')
                kb.approve(lid,'operator','synthetic-fixture-approval',row['content_hash'])
            self.assertTrue(complete(p)['project_complete'])
            p.section('A','Changed',origin='human')
            with self.assertRaises(ValueError):complete(p)
        finally:p.close()

    def test_project_facts_and_migration_idempotent(self):
        Project.init(self.root); p=Project(self.root)
        try:
            cfg=p.config(); cfg.update(schema_version=1,budget={'max_usd':2},execution={'workers':2})
            p.put('project','project.json',encoded(cfg),'human')
            p.put('fact:x','evidence/facts/x.json',encoded({'value':2}),'human')
            self.assertTrue(migrate(p)['migrated']); self.assertFalse(migrate(p)['migrated'])
            self.assertEqual(p.head('fact:x')['path'],'.ai/facts/x.json')
            self.assertNotIn('budget',p.config())
            self.assertTrue((self.root/'evidence/facts/x.json').exists())
        finally:p.close()

class LearningTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.root=Path(self.tmp.name)
        self.kb=Learning(self.root)
        self.data=dict(title='Missing source',rule='Facts need source and quote',
            evidence=[{'reference':'sanitized-case-1','quote':'Value had no source'}],author='author',
            cases=[{'input':{'facts':[{'value':2}]},'expected_findings':['missing_source'],
                    'explanation':'Reject unsupported numerical fact'}])
    def tearDown(self):self.kb.db.close();self.tmp.cleanup()
    def validated(self):
        r=self.kb.candidate(**self.data)
        return self.kb.validate(r['id'],'reviewer',True,True,True,'Confirmed generalized source requirement')
    def test_explicit_gate_and_shared_read(self):
        r=self.kb.candidate(**self.data)
        with self.assertRaises(ValueError): self.kb.approve(r['id'],'user','approval',r['content_hash'])
        with self.assertRaises(ValueError): self.kb.validate(r['id'],'author',True,True,True,'Self')
        r=self.validated()
        with self.assertRaises(ValueError):self.kb.approve(r['id'],'user','approval','stale-hash')
        self.kb.approve(r['id'],'user','user-message-123',r['content_hash'])
        with Learning(self.root) as other:
            self.assertEqual(other.snapshot()['snapshot'],self.kb.snapshot()['snapshot'])
            self.assertEqual(len(other.snapshot()['lessons']),1)
        self.assertEqual(len((self.root/'learning/LESSONS_LEDGER.jsonl').read_text(encoding='utf-8').splitlines()),3)

    def test_scope_no_global_storage_and_duplicate(self):
        before=(self.root/'learning/LESSONS_LEDGER.jsonl').read_bytes()
        self.assertFalse(self.kb.candidate(**{**self.data,'scope':'global'})['stored'])
        self.assertEqual(before,(self.root/'learning/LESSONS_LEDGER.jsonl').read_bytes())
        with self.assertRaises(ValueError): self.kb.candidate(**{**self.data,'scope':'project'})
        a=self.kb.candidate(**self.data);b=self.kb.candidate(**self.data)
        self.assertEqual(a,b)

    def test_cr_cannot_skip_test_and_deprecation_retains_history(self):
        r=self.validated()
        with self.assertRaises(ValueError):self.kb.change_request(r['id'],['skills/xh-qc/SKILL.md'],'author')
        self.kb.approve(r['id'],'user','approval',r['content_hash'])
        cr=self.kb.change_request(r['id'],['skills/xh-qc/SKILL.md'],'author')
        with self.assertRaises(ValueError):release(self.kb,cr['id'],'0.9.0','user','release-message')
        self.assertTrue(self.kb.evaluate()['passed'])
        self.kb.disposition(r['id'],'user','Superseded','deprecated')
        self.assertFalse(self.kb.snapshot()['lessons'])
        self.assertTrue((self.root/'knowledge/deprecated'/(r['id']+'.json')).exists())
        self.assertTrue(list((self.root/'learning/evaluation_cases').glob('*.json')))

    def test_failed_new_case_is_validation_evidence_but_blocks_release(self):
        data={**self.data,'cases':[{'input':{},'expected_findings':['new_rule'],
                                  'explanation':'New meaningful error to implement through approved CR'}]}
        r=self.kb.candidate(**data)
        self.kb.validate(r['id'],'reviewer',True,True,True,'Expected behavior reviewed')
        self.assertFalse(self.kb.evaluate()['passed'])

    def test_projection_recovers_from_interrupted_view(self):
        r=self.validated()
        (self.root/'learning/LESSONS_LEDGER.jsonl').write_text('partial',encoding='utf-8')
        with Learning(self.root) as other:
            self.assertEqual(other.get(r['id'])['status'],'validated')
        lines=(self.root/'learning/LESSONS_LEDGER.jsonl').read_text(encoding='utf-8').splitlines()
        self.assertEqual(len(lines),2)
        for line in lines:json.loads(line)

    def test_deleting_or_weakening_case_cannot_pass(self):
        r=self.validated()
        file=self.root/'learning/evaluation_cases'/(r['id']+'-0.json')
        file.write_bytes(encoded({'input':{},'expected_findings':[],'explanation':'weakened'}))
        self.assertFalse(self.kb.evaluate()['passed'])
        file.unlink()
        self.assertFalse(self.kb.evaluate()['passed'])

if __name__=='__main__':unittest.main()
