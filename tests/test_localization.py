import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'tools'))
import setup
import release_check


class LocalizationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='raven-language-')
        self.addCleanup(self.tmp.cleanup)
        self.vault = (Path(self.tmp.name)/'vault').resolve()
        with patch.object(setup, 'find_cli', return_value=''):
            setup.install(self.vault, language='en', conversation_language='tr', summary_language='tr')

    def run_code(self, code):
        result = subprocess.run([sys.executable, '-c', code], cwd=self.vault/'00-System/Scripts', capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout

    def read(self, relative):
        return (self.vault/relative).read_text(encoding='utf-8')

    def test_catalog_parity_and_english_install(self):
        en = json.loads(self.read('00-System/Locales/en.json'))
        tr = json.loads(self.read('00-System/Locales/tr.json'))
        for section in ('documents', 'messages', 'bases'):
            self.assertEqual(set(en[section]), set(tr[section]))
        self.assertIn('Shared memory', self.read('Dashboard.md'))
        self.assertIn('Model calls today:', self.read('00-System/Memory-Status.md'))
        self.assertIn('## Action', self.read('00-System/Templates/Task.md'))
        self.assertNotIn('## Eylem', self.read('00-System/Templates/Task.md'))

    def test_switch_preserves_data_ids_filters_and_independent_preferences(self):
        note = self.vault/'01-Inbox/personal.md'
        note.write_text('Karar: Türkçe kalacak. Shared memory. Kullanıcı.', encoding='utf-8')
        before = note.read_bytes()
        settings = json.loads(self.read('00-System/Config/settings.json'))
        dashboard_meta = self.read('Dashboard.md').split('---\n')[1]
        base_before = json.loads(self.read('00-System/Bases/Today.base'))
        self.run_code("import localization as l;l.change('tr')")
        self.assertIn('Ortak hafıza', self.read('Dashboard.md'))
        self.assertEqual(note.read_bytes(), before)
        self.assertEqual(dashboard_meta, self.read('Dashboard.md').split('---\n')[1])
        updated = json.loads(self.read('00-System/Config/settings.json'))
        self.assertEqual(updated, dict(settings, language='tr'))
        base_after = json.loads(self.read('00-System/Bases/Today.base'))
        self.assertEqual(base_before['filters'], base_after['filters'])
        self.assertEqual(base_before['views'][0]['order'], base_after['views'][0]['order'])
        self.assertEqual(set(base_before['properties']), set(base_after['properties']))
        self.run_code("import localization as l;l.change('en')")
        self.assertEqual(note.read_bytes(), before)

    def test_edited_page_aborts_without_partial_writes(self):
        p = self.vault/'Dashboard.md'
        p.write_text(p.read_text(encoding='utf-8')+'\nMy custom link\n', encoding='utf-8')
        before = {p:p.read_bytes() for p in self.vault.rglob('*') if p.is_file()}
        self.run_code("import localization as l\ntry:l.change('tr')\nexcept ValueError as e:assert 'nothing changed' in str(e)\nelse:raise AssertionError('edited page overwritten')")
        self.assertEqual(before, {p:p.read_bytes() for p in before})

    def test_invalid_language_writes_nothing(self):
        target = self.vault.parent/'invalid'
        with self.assertRaisesRegex(ValueError, 'Unsupported'):
            setup.install(target, language='de')
        self.assertFalse(target.exists())

    def test_summary_language_and_verbatim_source(self):
        output = self.run_code("import memory_worker as w,localization as l,json\nr=[dict(id='test',project='general',prompt='Karar: kaynak Türkçe kalır.',answer='Evet.')]; print(w.prompt(r)); l.change(summary='en'); print(w.prompt(r))")
        self.assertIn('Türkçe özet ve konu adları', output)
        self.assertIn('İngilizce özet ve konu adları', output)
        self.assertEqual(output.count('Karar: kaynak Türkçe kalır.'), 2)
        self.assertIn('kaynak dilinde birebir koru', output)

    def test_english_wrappers_preserve_stored_summary_and_evidence(self):
        output = self.run_code("""import memory_engine as m,brain,json,time,uuid
sid=str(uuid.uuid4()); rid=str(uuid.uuid4())
with m.database() as con:
 con.execute('INSERT INTO sessions(id,provider,external_id,updated) VALUES (?,?,?,?)',(sid,'codex','test',time.time()))
 payload=dict(summary='Türkçe karar korunur.',evidence=[dict(role='user',kind='decision',quote='Kaynak Türkçe kalır.')],topics=[],provider='codex')
 con.execute('INSERT INTO memories VALUES (?,?,?,?,?)',(rid,sid,'general',json.dumps(payload,ensure_ascii=False),time.time()))
m.publish()
print((brain.ROOT/m.SESSION_DIR/(sid+'.md')).read_text(encoding='utf-8'))
""")
        self.assertIn('# Session memory', output)
        self.assertIn('**User / decision:** Kaynak Türkçe kalır.', output)
        self.assertIn('Türkçe karar korunur.', output)

    def test_conversation_preference_does_not_enable_capture(self):
        result = self.run_code("import raven_hook as h,brain,json;print(json.dumps(h.handle(dict(cwd=str(brain.ROOT),session_id='test',hook_event_name='SessionStart')),ensure_ascii=False))")
        self.assertIn('respond in Turkish', result)
        self.assertFalse(json.loads(self.read('00-System/Config/memory.json'))['enabled'])

    def test_icons_are_valid_and_trailing_payload_rejected(self):
        for relative in release_check.ICON_PATHS:
            data = (setup.REPO/relative).read_bytes()
            self.assertTrue(release_check.valid_icon(data))
            self.assertFalse(release_check.valid_icon(data+b'not an image'))


if __name__ == '__main__':
    unittest.main()
