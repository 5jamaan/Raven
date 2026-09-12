"""Codex/Claude Code adapters. Never request an agent continuation."""
from i18n import t
from i18n import conversation_instruction
import json, os, sys
from pathlib import Path
import memory_engine as mem

def claude_current(event, sid):
    """Version-sensitive fallback only for Claude's missing turn identifier.
    Read the named transcript in memory, never copy it. Match the actual latest
    user text to the pending event; a read-only or excluded turn cannot reuse it.
    """
    path=Path(event.get('transcript_path') or '')
    allowed_root=Path.home()/'.claude/projects'
    if not path.is_file() or not path.resolve().is_relative_to(allowed_root.resolve()): return None
    if path.suffix!='.jsonl' or path.is_symlink(): return None
    with path.open('rb') as f:
        size=f.seek(0,2); f.seek(max(0,size-2_000_000)); data=f.read()
    lines=data.splitlines()
    if size>2_000_000: lines=lines[1:]
    last_user=None; last_assistant=''
    for line in lines:
        try: row=json.loads(line)
        except ValueError: continue
        msg=row.get('message',{}); content=msg.get('content','')
        if isinstance(content,dict): content=content.get('text','') if content.get('type')=='text' else ''
        if isinstance(content,list): content='\n'.join(b.get('text','') for b in content if isinstance(b,dict) and b.get('type')=='text')
        if not isinstance(content,str) or not content: continue
        if row.get('type')=='user' and not row.get('isMeta'):
            last_user=content; last_assistant=''
        elif row.get('type')=='assistant': last_assistant=content
    if not last_user or mem.excluded_prompt(last_user): return None
    with mem.database(True) as con:
        row=con.execute('SELECT * FROM turns WHERE session=? AND status="pending" ORDER BY created DESC LIMIT 1',(sid,)).fetchone()
    if not row or row['prompt']!=mem.clean(last_user): return None
    return dict(event,turn_id=row['external_turn'],last_assistant_message=event.get('last_assistant_message') or last_assistant)

def handle(event,provider='codex'):
    if os.environ.get('RAVEN_MEMORY_WORKER') or not mem.in_scope(event.get('cwd')): return {}
    if provider not in ('codex','claude') or not event.get('session_id'): return {}
    kind=event.get('hook_event_name'); sid=mem.key(provider,event['session_id'])
    if kind=='SessionStart':
        context=conversation_instruction()+mem.context(provider,event['session_id'])
        return {'hookSpecificOutput':{'hookEventName':kind,'additionalContext':context}} if context else {}
    if kind=='UserPromptSubmit':
        prompt=event.get('prompt','')
        if not isinstance(prompt,str) or mem.READ_ONLY.search(prompt): return {}
        if mem.NO_CAPTURE.search(prompt):
            # Store only the opt-out switch, never this message. This persists
            # for the whole conversation; a later message cannot re-enable it.
            if mem.config()['enabled']:
                with mem.database() as con:
                    con.execute('INSERT OR IGNORE INTO sessions(id,provider,external_id,disabled,updated) VALUES (?,?,?,?,?)',(sid,provider,event['session_id'],1,mem.time.time()))
                    con.execute('UPDATE sessions SET disabled=1 WHERE id=?',(sid,))
            return {'hookSpecificOutput':{'hookEventName':kind,'additionalContext':t('Bu sohbet için Raven otomatik kaydı kapalı. Bu mesajın içeriği kaydedilmedi. Daha önceki kayıtlar silinmedi.')}}
        tid=mem.capture_prompt(event,provider)
        if not tid: return {}
        return {'hookSpecificOutput':{'hookEventName':kind,'additionalContext':
            t('Raven oturum kimliği: ')+sid+t('. Hafıza otomatik kuyruğa alınır; devir yazmak için ek araç çağırma. Kullanıcının salt okunur/kaydetme talimatı her zaman önceliklidir.\n')+mem.context(provider,event['session_id'],prompt)}}
    if kind=='Stop':
        if provider=='claude':
            if not (mem.DATA/'memory.sqlite3').exists(): return {}
            event=claude_current(event,sid)
            if not event: return {}
        mem.finish_turn(event,provider)
    # End/interrupt/compaction never force a model round-trip or store transcripts.
    # Pending prompts remain visible until a final answer or the retention limit.
    return {}

if __name__=='__main__':
    if hasattr(sys.stdin,'reconfigure'): sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    try: print(json.dumps(handle(json.load(sys.stdin),sys.argv[1] if len(sys.argv)>1 else 'codex'),ensure_ascii=False))
    except Exception:
        print(json.dumps({'systemMessage':t('Raven otomatik kaydı tamamlanamadı; hafıza durumunu kontrol et.')}))
