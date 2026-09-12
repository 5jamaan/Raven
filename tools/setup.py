"""Create a NEW private vault from the public template. Never modify an existing vault."""
import argparse
import json
import os
from pathlib import Path
import shlex
import shutil
import subprocess
import sys
import uuid

REPO = Path(__file__).resolve().parents[1]

def find_cli(provider):
    direct = shutil.which(provider)
    if direct:
        return str(Path(direct).resolve())
    local = Path(os.environ.get('LOCALAPPDATA', str(Path.home())))
    pattern = ('OpenAI/Codex/bin/*/codex.exe' if provider == 'codex' else
               'Packages/Claude_*/LocalCache/Roaming/Claude/claude-code/*/claude.exe')
    candidates = list(local.glob(pattern))
    return str(max(candidates, key=lambda p: p.stat().st_mtime)) if candidates else ''

def command(parts):
    if os.name == 'nt':
        # Windows hook hosts use a shell. Refuse shell expansion characters.
        if any(any(c in p for c in '%!&|<>^"\r\n') for p in parts):
            raise ValueError('Use paths without Windows shell metacharacters.')
        return subprocess.list2cmdline(parts)
    return shlex.join(parts)

def install(vault, user='User', runner='codex', model='', enable=False, codex='', claude=''):
    vault = Path(vault).expanduser().resolve()
    if vault.exists():
        raise ValueError('Target already exists. Choose a NEW folder; nothing was overwritten.')
    if vault.is_relative_to(REPO):
        raise ValueError('Keep your private vault outside the public source repository.')
    executables = {'codex': codex or find_cli('codex'), 'claude': claude or find_cli('claude')}
    if enable and (not model or not executables[runner] or not Path(executables[runner]).is_file()):
        raise ValueError('Enabling cloud memory requires an available runner executable and explicit model.')
    python = str(Path(sys.executable).resolve())
    # Validate hook paths before copying anything.
    command([python, str(vault/'00-System/Scripts/lifecycle.py')])
    shutil.copytree(REPO/'template', vault, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
    shutil.copyfile(REPO/'tools/vault.gitignore',vault/'.gitignore')
    config = vault/'00-System/Config'
    settings = json.loads((config/'settings.json').read_text(encoding='utf-8'))
    settings.update(user=user, python=python)
    (config/'settings.json').write_text(json.dumps(settings, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    memory = json.loads((config/'memory.json').read_text(encoding='utf-8'))
    memory.update(enabled=enable, cloud_processing=enable, runner=runner, model=model,
                  codex_path=executables['codex'], claude_path=executables['claude'])
    (config/'memory.json').write_text(json.dumps(memory, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    # Fresh note IDs make independently installed vaults independent records.
    for path in vault.rglob('*.md'):
        text=path.read_text(encoding='utf-8')
        if text.startswith('---\n') and '\nid: ' in text:
            import re
            text=re.sub(r'(?m)^id: .*$', 'id: "'+str(uuid.uuid4())+'"', text, count=1)
            path.write_text(text,encoding='utf-8')
    for provider in ('codex', 'claude'):
        path=vault/('.codex' if provider=='codex' else '.claude');path.mkdir(exist_ok=True)
        parts=[python,str(vault/'00-System/Scripts'/('lifecycle.py' if provider=='codex' else 'raven_hook.py'))]
        if provider=='claude':parts.append('claude')
        entry={'type':'command','command':command(parts),'timeout':15}
        if provider=='codex': entry['commandWindows']=command(parts)
        events=['SessionStart','UserPromptSubmit','Stop','SessionEnd','PreCompact']
        if provider=='codex':events.append('Interrupt')
        content={'hooks':{event:[{'hooks':[entry.copy()]}] for event in events}}
        target=path/('hooks.json' if provider=='codex' else 'settings.json')
        target.write_text(json.dumps(content,indent=2)+'\n',encoding='utf-8')
    # Only initialize local generated pages; never run a model or install a task.
    code="import memory_engine as m;m.publish();m.render_status()"
    init=subprocess.run([python,'-c',code],cwd=vault/'00-System/Scripts',capture_output=True,text=True)
    if init.returncode:
        raise RuntimeError('Vault copied but status initialization failed. Inspect locally; no existing vault was changed.')
    return vault

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--vault',required=True)
    parser.add_argument('--user',default='User')
    parser.add_argument('--runner',choices=['codex','claude'],default='codex')
    parser.add_argument('--model',default='')
    parser.add_argument('--codex',default='')
    parser.add_argument('--claude',default='')
    parser.add_argument('--enable-memory',action='store_true',help='Explicitly allow captured turns to be processed by the selected cloud model, including turns from the other provider.')
    args=parser.parse_args()
    try:
        vault=install(args.vault,args.user,args.runner,args.model,args.enable_memory,args.codex,args.claude)
    except (ValueError,RuntimeError) as exc:
        parser.exit(1,str(exc)+'\n')
    print('Created: '+str(vault))
    print('Cloud memory: '+('enabled with your explicit choice' if args.enable_memory else 'OFF'))
    print('Review hooks in Codex/Claude Code. No scheduler, external account or Git remote was installed.')

if __name__=='__main__':main()
