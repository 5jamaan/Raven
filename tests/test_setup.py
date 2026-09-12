import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
import setup
import release_check

class SetupTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='raven-install-test-');self.addCleanup(self.tmp.cleanup)
        self.target=(Path(self.tmp.name)/'new vault').resolve()
        p=patch.object(setup,'find_cli',return_value='');p.start();self.addCleanup(p.stop)

    def test_safe_default_install(self):
        setup.install(self.target)
        memory=json.loads((self.target/'00-System/Config/memory.json').read_text())
        self.assertFalse(memory['enabled']);self.assertFalse(memory['cloud_processing'])
        conf=json.loads((self.target/'00-System/Config/settings.json').read_text())
        self.assertFalse(conf['mem0']['enabled']);self.assertFalse(conf['todoist']['enabled'])
        self.assertTrue((self.target/'85-Companion/Memory-Index.md').exists())
        self.assertIn('85-Companion/',(self.target/'.gitignore').read_text())
        hooks=json.loads((self.target/'.codex/hooks.json').read_text())['hooks']
        self.assertIn(str(self.target),hooks['Stop'][0]['hooks'][0]['command'])
        self.assertFalse((self.target/'00-System/State').exists())
        checked=subprocess.run([sys.executable,str(self.target/'00-System/Scripts/brain.py'),'doctor'],capture_output=True,text=True,encoding='utf-8')
        self.assertEqual(checked.returncode,0,checked.stderr)
        self.assertEqual(json.loads(checked.stdout)['failures'],0,checked.stdout)

    def test_existing_folder_never_overwritten(self):
        self.target.mkdir();p=self.target/'my-note.md';p.write_text('keep')
        with self.assertRaisesRegex(ValueError,'already exists'):setup.install(self.target)
        self.assertEqual(p.read_text(),'keep');self.assertEqual(len(list(self.target.iterdir())),1)

    def test_public_repo_cannot_be_private_vault(self):
        with self.assertRaisesRegex(ValueError,'outside'):setup.install(setup.REPO/'private-vault')

    def test_cloud_enable_requires_explicit_model_and_executable(self):
        with self.assertRaisesRegex(ValueError,'requires'):setup.install(self.target,enable=True)
        self.assertFalse(self.target.exists())

    def test_windows_shell_expansion_rejected(self):
        with self.assertRaisesRegex(ValueError,'metacharacters'):setup.command(['python.exe','bad%PATH%/hook.py'])

    def test_release_guard_rejects_personal_state_and_secrets(self):
        self.assertIn('runtime or secret-bearing file',release_check.inspect('template/85-Companion/Sessions/a.md','hello'))
        self.assertIn('possible credential',release_check.inspect('file.txt','sk-'+'X'*30))
        sample='C:'+chr(92)+'Users'+chr(92)+'someone'+chr(92)+'secret.txt'
        self.assertIn('personal machine path',release_check.inspect('file.txt',sample))

if __name__=='__main__':unittest.main()
