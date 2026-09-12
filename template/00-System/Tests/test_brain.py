import sys,unittest,tempfile,json,uuid,shutil
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Scripts'))
import brain,gateway,lifecycle

class BrainTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(); self.old=(brain.ROOT,brain.CONFIG,brain.STATE)
        brain.ROOT=Path(self.temp.name); brain.CONFIG=brain.ROOT/'00-System/Config'; brain.STATE=brain.ROOT/'00-System/State'; brain.CONFIG.mkdir(parents=True)
        for filename in ('settings.json','folder-policies.json'): shutil.copy(self.old[1]/filename,brain.CONFIG/filename)
        (brain.ROOT/'85-Companion').mkdir()
        for name in ('Core','Rules','Last-Session','Threads','Journal'):
            shutil.copy(self.old[0]/f'85-Companion/{name}.md',brain.ROOT/f'85-Companion/{name}.md')
    def tearDown(self): brain.ROOT,brain.CONFIG,brain.STATE=self.old; self.temp.cleanup()
    def make(self,path,body='Genel çalışma bilgisi',**kw):
        m=brain.metadata(**kw); brain.write_new(path,brain.serialize(m,'\n# Kayıt\n\n'+body)); return path,m
    def source(self): return self.make('60-Knowledge/source.md',privacy='shareable')
    def atom(self,privacy='shareable',**kw):
        _,s=self.source(); defaults=dict(kind='memory-candidate',privacy=privacy,memory_eligible=True,status='approved',confidence='confirmed',memory_atom='Kısa ve doğrudan Türkçe yanıtları tercih eder.',source_id=s['id']); defaults.update(kw)
        return self.make('60-Knowledge/atom.md',**defaults)[0]
    def task(self,privacy='shareable',**kw):
        d=dict(kind='task',privacy=privacy,task_id=str(uuid.uuid4()),todoist_sync=True,export_text='Öğrenme notunu gözden geçir',status='open',due='2026-09-12'); d.update(kw)
        return self.make('01-Inbox/task.md',**d)[0]
    def test_shareable_atom_passes(self): self.assertEqual(brain.export_record(self.atom(),'mem0')['payload']['infer'],False)
    def test_private_mem0_blocked(self):
        with self.assertRaises(ValueError): brain.export_record(self.atom('private'),'mem0')
    def test_private_task_generic(self): self.assertEqual(brain.export_record(self.task('private'),'todoist')['payload']['content'],'Özel bir görevi gözden geçir')
    def test_denied_ai_blocked(self):
        with self.assertRaises(ValueError): brain.export_record(self.task(ai_access='denied'),'todoist')
    def test_noneligible_blocked(self):
        with self.assertRaises(ValueError): brain.export_record(self.atom(memory_eligible=False),'mem0')
    def test_unconfirmed_blocked(self):
        with self.assertRaises(ValueError): brain.export_record(self.atom(confidence='inferred'),'mem0')
    def test_fake_key_blocks_capture(self):
        f=brain.ROOT/'input.txt'; f.write_text('sk-'+'z'*24)
        with self.assertRaises(ValueError): brain.capture(f,'note')
        self.assertFalse((brain.ROOT/'01-Inbox').exists())
    def test_mem0_key_pattern_blocked(self): self.assertTrue(brain.has_secret('m0-'+'Z'*40))
    def test_body_secret_blocks_safe_title(self):
        path=self.task(); p=brain.ROOT/path; p.write_text(p.read_text()+'\nsk-'+'x'*24)
        with self.assertRaises(ValueError): brain.export_record(path,'todoist')
    def test_sensitive_title_blocks_mem0(self):
        path=self.atom(); target=brain.ROOT/'60-Knowledge/kimlik numarası.md'; (brain.ROOT/path).rename(target)
        with self.assertRaises(ValueError): brain.export_record(target,'mem0')
    def test_source_reclassified_blocks(self):
        path=self.atom(); p=brain.ROOT/'60-Knowledge/source.md'; p.write_text(p.read_text().replace('privacy: "shareable"','privacy: "private"'))
        with self.assertRaises(ValueError): brain.export_record(path,'mem0')
    def test_no_body_export(self): self.assertNotIn('Genel çalışma bilgisi',json.dumps(brain.export_record(self.task(),'todoist')['payload']))
    def test_path_escape(self):
        with self.assertRaises(ValueError): brain.safe_path('../escape.md')
    def test_yaml_duplicate_rejected(self):
        p=brain.ROOT/'bad.md'; p.write_text('---\nprivacy: private\nprivacy: shareable\n---\ntext')
        with self.assertRaises(ValueError): brain.parse_note(p)
    def test_yaml_complex_rejected(self):
        p=brain.ROOT/'bad.md'; p.write_text('---\nprivacy: [private\n---\ntext')
        with self.assertRaises(ValueError): brain.parse_note(p)
    def test_claim_ack_duplicate(self):
        path=self.task(); first=gateway.claim(path); gateway.ack(first['record'],'remote-test',first['hash']); self.assertEqual(gateway.claim(path)['status'],'duplicate-skipped')
    def test_unknown_send_not_retried(self):
        path=self.task(); gateway.claim(path)
        with self.assertRaises(ValueError): gateway.claim(path)
    def test_ack_wrong_hash_rejected(self):
        first=gateway.claim(self.task())
        with self.assertRaises(ValueError): gateway.ack(first['record'],'remote','wrong')
    def test_strict_local_context_excludes_private(self):
        conf=brain.settings(); conf['private_ai_access']='strict-local'; (brain.CONFIG/'settings.json').write_text(json.dumps(conf)); self.assertEqual(brain.context(),'')
    def test_context_excludes_journal(self): self.assertNotIn('Raven ile yolculuk',brain.context()); self.assertNotIn('## Closed',brain.context())
    def test_no_overwrite_capture(self):
        self.make('existing.md')
        with self.assertRaises(FileExistsError): brain.write_new('existing.md','overwrite')
    def test_session_requires_approval(self):
        with self.assertRaises(ValueError): brain.session_close({'summary':'test','next_step':'devam'})
    def test_session_updates_and_archives(self):
        brain.session_close({'summary':'Test oturumu','next_step':'Testleri sürdür','milestone':'Önemli test dönüm noktası','threads':'Tür: araştırma; Durum: active; Neden açık: test; Son gelişme: denendi; Sonraki adım: doğrula; İlgili notlar: Last-Session; Tarih: 2026-09-12; Gözden geçirme: 2026-09-13','turn_id':'test-turn'},True)
        self.assertIn('Test oturumu',(brain.ROOT/'85-Companion/Last-Session.md').read_text(encoding='utf-8'))
        self.assertIn('Önemli test dönüm noktası',(brain.ROOT/'85-Companion/Journal.md').read_text(encoding='utf-8'))
        self.assertEqual(lifecycle.handle({'cwd':str(brain.ROOT),'hook_event_name':'Stop','turn_id':'test-turn'}),{})
        self.assertTrue(list((brain.ROOT/'00-System/Logs/Sessions').glob('*previous.md')))
    def test_stop_never_restarts_agent_or_writes_missing_trace(self):
        event={'cwd':str(brain.ROOT),'hook_event_name':'Stop','turn_id':'test'}
        self.assertEqual(lifecycle.handle(event),{})
        event['stop_hook_active']=True
        self.assertEqual(lifecycle.handle(event),{})
        self.assertFalse(list((brain.ROOT/'00-System/Logs/Sessions').glob('*incomplete.md')))
    def test_reviews_can_be_created_without_network(self):
        self.assertTrue((brain.ROOT/brain.review('daily')).exists()); self.assertTrue((brain.ROOT/brain.review('weekly')).exists())
    def test_project_missing_next_action_detected(self):
        self.make('30-Projects/p.md',kind='project',status='active',next_action='')
        self.assertTrue(any(h['reason']=='Sonraki adım eksik' for h in brain.findings()))
    def test_policy_change_invalidates_approval(self):
        first=brain.policy_hash(); conf=brain.settings(); conf['sensitive_terms']=['hassasproje']; (brain.CONFIG/'settings.json').write_text(json.dumps(conf)); self.assertNotEqual(first,brain.policy_hash())
if __name__=='__main__': unittest.main(verbosity=2)
