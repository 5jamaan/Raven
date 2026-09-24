import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'Scripts'))
import brain, vault_io, memory_engine as mem, memory_worker as worker
import gateway


class ReliabilityTests(unittest.TestCase):

    def setUp(self):
        temp = tempfile.TemporaryDirectory(prefix='raven-reliability-')
        self.addCleanup(temp.cleanup)
        self.base = Path(temp.name)
        self.root = self.base / 'vault'
        self.root.mkdir()
        original = brain.CONFIG
        for obj, name, value in ((brain, 'ROOT', self.root), (brain, 'CONFIG', self.root / '00-System/Config'), (brain, 'STATE', self.root / '00-System/State'), (mem, 'DATA', self.base / 'memory'), (mem, 'CONFIG', self.root / '00-System/Config/memory.json')):
            p = patch.object(obj, name, value)
            p.start()
            self.addCleanup(p.stop)
        brain.CONFIG.mkdir(parents=True)
        for name in ('settings.json', 'folder-policies.json', 'memory.json'):
            shutil.copy(original / name, brain.CONFIG / name)
        self.env = patch.dict(os.environ, {'LOCALAPPDATA': str(self.base / 'local')})
        self.env.start()
        self.addCleanup(self.env.stop)
        for name in ('85-Companion/Threads.md', '00-System/Status.md'):
            brain.write_new(name, brain.serialize(brain.metadata('system'), '\n# Status\n'))

    def note(self, path, body='ordinary note'):
        brain.write_new(path, brain.serialize(brain.metadata(), body))

    def junction(self, target, path):
        if os.name == 'nt':
            result = subprocess.run(['cmd', '/c', 'mklink', '/J', str(path), str(target)], capture_output=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.addCleanup(lambda: os.rmdir(path) if path.exists() else None)
        else:
            path.symlink_to(target, target_is_directory=True)

    def test_walk_prunes_temp_dependencies_and_caches(self):
        self.note('01-Inbox/real.md')
        for folder in ('tmp', 'node_modules', '.git', '__pycache__', '.venv', 'nested/node_modules'):
            p = self.root / folder / 'bad.md'
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text('not a note')
        paths = {p.relative_to(self.root).as_posix() for p in brain.records()}
        self.assertIn('01-Inbox/real.md', paths)
        self.assertFalse(any((p.endswith('bad.md') for p in paths)))

    def test_junctions_never_enter_scan_export_or_backup(self):
        external = self.base / 'outside'
        external.mkdir()
        (external / 'private.md').write_text('external-private')
        alias = self.root / 'linked'
        self.junction(external, alias)
        self.assertFalse(any((p.name == 'private.md' for p in vault_io.files(self.root))))
        for action in (lambda: brain.safe_path(alias / 'private.md'), lambda: brain.export_record('linked/private.md', 'mem0')):
            with self.assertRaises(ValueError):
                action()
        archive = brain.backup()
        with zipfile.ZipFile(archive) as z:
            self.assertFalse(any((n.startswith('linked/') for n in z.namelist())))
        self.assertEqual((external / 'private.md').read_text(), 'external-private')

    def test_internal_junction_rejected_too(self):
        target = self.root / 'real'
        target.mkdir()
        self.junction(target, self.root / 'alias')
        with self.assertRaises(ValueError):
            brain.safe_path('alias/new.md')

    def test_explicit_excluded_path_and_escape_rejected(self):
        for value in ('tmp/new.md', 'nested/NODE_MODULES/new.md', '../outside.md'):
            with self.assertRaises(ValueError):
                brain.safe_path(value)

    def test_github_revision_is_not_a_secret(self):
        sha = 'a1' * 20
        for kind in ('commit', 'tree', 'blob'):
            text = f'https://github.com/example/project/{kind}/{sha}/file.md'
            self.assertFalse(brain.has_secret(text))
            self.assertEqual(mem.clean(text), text)

    def test_secret_exception_is_limited_to_revision_component(self):
        sha = 'a1' * 20
        for text in (sha, 'password=' + sha, 'https://evil.test/github.com/x/y/tree/' + sha, 'https://github.com.evil.test/x/y/tree/' + sha, 'https://github.com/x/y/tree/main/' + sha, 'https://github.com/x/y/tree/' + sha + '?token=' + sha, 'https://github.com/x/y/tree/' + sha + '00', 'api_key=https://github.com/x/y/tree/' + sha):
            self.assertTrue(brain.has_secret(text), text)
        self.assertTrue(brain.has_secret('https://github.com/x/y/tree/' + sha + ' sk-' + 'x' * 24))

    def test_failed_backup_never_leaves_a_success_zip(self):
        self.note('01-Inbox/secret.md', 'sk-' + 'x' * 24)
        with self.assertRaises(ValueError):
            brain.backup()
        self.assertEqual(list((brain.runtime_dir() / 'Backups').iterdir()), [])

    def test_backup_sqlite_is_consistent_and_readable(self):
        with brain.db() as con:
            con.execute('INSERT INTO runs VALUES (?,?)', ('test', brain.now()))
        target = brain.backup()
        with zipfile.ZipFile(target) as archive:
            self.assertIsNone(archive.testzip())
            self.assertIn('00-System/State/state.sqlite3', archive.namelist())
            self.assertNotIn('00-System/State/state.sqlite3-wal', archive.namelist())
