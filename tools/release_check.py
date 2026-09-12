"""Read-only publication checks. Never print matched secret values."""
import json
from pathlib import Path
import re
import subprocess
import sys
import struct

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'template/00-System/Scripts'))
import brain

ICON_PATHS = {'template/00-System/Assets/raven-terminal.ico', 'template/00-System/Assets/raven-dashboard.ico'}

def valid_icon(data):
    """Allow only bounded ICO image entries, with no appended data or gaps."""
    try:
        reserved, kind, count = struct.unpack_from('<HHH', data)
        if reserved or kind != 1 or not 1 <= count <= 32:
            return False
        cursor = 6+16*count
        entries = sorted(struct.unpack_from('<II',data,6+16*i+8) for i in range(count))
        entries.sort(key=lambda item:item[1])
        for size, offset in entries:
            if offset != cursor or size < 40 or offset+size > len(data):
                return False
            image = data[offset:offset+size]
            if not (image.startswith(b'\x89PNG\r\n\x1a\n') or image[:4] == b'\x28\x00\x00\x00'):
                return False
            cursor += size
        return cursor == len(data)
    except (struct.error, ValueError):
        return False

def inspect(path, content):
    issues=[]
    name=path.replace('\\','/')
    if any(part in name.split('/') for part in ('State','Logs','Sessions','Derived')) or name.endswith(('.sqlite3','.db','.zip','.jsonl','.key','.pem')):
        issues.append('runtime or secret-bearing file')
    if Path(name).name.startswith('.env'):
        issues.append('environment file')
    # Immutable upstream action pins are public dependency identifiers.
    scan=re.sub(r'(?m)^\s*- uses: actions/(?:checkout|setup-python)@[0-9a-f]{40}[^\n]*$', '', content) if name=='.github/workflows/tests.yml' else content
    if brain.has_secret(scan):issues.append('possible credential')
    if re.search(r'(?i)[a-z]:[\\/]+Users[\\/]+(?!Public\b)',content):issues.append('personal machine path')
    return issues

def main():
    result=subprocess.run(['git','ls-files','-z'],cwd=ROOT,capture_output=True)
    if result.returncode:
        print('Initialize/stage the public repository before the release check.');return 1
    files=[p for p in result.stdout.decode('utf-8').split('\0') if p]
    if not files:print('No tracked files to inspect.');return 1
    failed=[]
    for relative in files:
        p=ROOT/relative
        if p.is_symlink():failed.append((relative,'symlink'));continue
        if relative in ICON_PATHS:
            if not valid_icon(p.read_bytes()):failed.append((relative,'invalid ICO image'))
            continue
        try:body=p.read_text(encoding='utf-8')
        except (OSError,UnicodeError):failed.append((relative,'unreadable/non-text file'));continue
        failed.extend((relative,error) for error in inspect(relative,body))
    try:
        conf=json.loads((ROOT/'template/00-System/Config/settings.json').read_text(encoding='utf-8'))
        memory=json.loads((ROOT/'template/00-System/Config/memory.json').read_text(encoding='utf-8'))
        assert not conf['mem0']['enabled'] and not conf['mem0']['user_id'] and not conf['mem0']['policy_approval']
        assert not conf['todoist']['enabled'] and not conf['todoist']['project_id'] and not conf['todoist']['sections']
        assert not conf['todoist']['iphone_verified'] and not conf['python']
        assert not memory['enabled'] and not memory['cloud_processing'] and not memory['codex_path'] and not memory['claude_path']
    except (AssertionError,KeyError,ValueError):failed.append(('template configuration','must be disabled and account-free'))
    for path,reason in failed:print(path+': '+reason)
    if failed:return 1
    print(f'{len(files)} public files checked: no known secrets, private runtime files or personal machine paths.');return 0

if __name__=='__main__':sys.exit(main())
