"""Only network gateway. Todoist OAuth uses a filtered claim/ack outbox."""
import argparse, json, sys, uuid, urllib.request, urllib.error
from pathlib import Path
import brain
from credential_store import read

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self,*args,**kwargs): raise ValueError('API yönlendirmesi engellendi')
def request(method,path,payload=None):
    if not path.startswith(('/v3/memories/','/v1/memories/','/v1/event/')): raise ValueError('İzin verilmeyen Mem0 yolu')
    token=read('mem0')
    req=urllib.request.Request('https://api.mem0.ai'+path,data=None if payload is None else json.dumps(payload).encode(),method=method,headers={'Authorization':'Token '+token,'Content-Type':'application/json'})
    try:
        with urllib.request.build_opener(NoRedirect).open(req,timeout=25) as response:
            content=response.read(); return json.loads(content) if content else {}
    except urllib.error.HTTPError as error:
        brain.audit('http',service='mem0',code=error.code,status='error')
        raise ValueError('Mem0 HTTP '+str(error.code)+'; yanıt içeriği gizlendi') from None
    except urllib.error.URLError:
        brain.audit('http',service='mem0',status='unavailable'); raise ValueError('Mem0 erişilemiyor; yerel notlar korunuyor') from None
def mark(r,status,remote=''):
    with brain.db() as con: con.execute('INSERT OR REPLACE INTO sync VALUES (?,?,?,?,?,?)',(r['service'],r['record'],r['hash'],remote,status,brain.now()))
    brain.audit('sync',service=r['service'],record=r['record'],hash=r['hash'],status=status)
def state(r):
    with brain.db() as con: return con.execute('SELECT hash,remote,status FROM sync WHERE service=? AND record=?',(r['service'],r['record'])).fetchone()
def preview(service):
    accepted=[]; blocked=0
    for p in brain.records():
        try:
            m,_,_=brain.parse_note(p)
            if service=='mem0' and m.get('type')!='memory-candidate': continue
            if service=='todoist' and not m.get('todoist_sync'): continue
            r=brain.export_record(p,service); previous=state(r)
            if previous and previous[2]=='deleted': continue
            if previous and previous[0]==r['hash'] and previous[2]=='ok': continue
            accepted.append(r)
        except ValueError: blocked+=1
    return {'policy_hash':brain.policy_hash(),'accepted':accepted,'blocked_count':blocked}
def mem0_sync():
    conf=brain.settings()
    if not conf['mem0']['enabled'] or conf['mem0']['policy_approval']!=brain.policy_hash(): raise ValueError('Mem0 politika onayı eksik veya değişmiş')
    with brain.lock('mem0-sync'):
        batch=preview('mem0')['accepted'][:conf['mem0']['max_atoms_per_run']]
        for r in batch:
            previous=state(r)
            atom_hash=brain.digest(' '.join(r['payload']['messages'][0]['content'].casefold().split()))
            with brain.db() as con: duplicate=con.execute('SELECT record FROM fingerprints WHERE service=? AND hash=?',('mem0',atom_hash)).fetchone()
            if duplicate and duplicate[0]!=r['record']:
                brain.audit('memory-duplicate',service='mem0',record=r['record'],status='skipped'); continue
            if previous and previous[2] not in ('ok','deleted'): raise ValueError('Önce belirsiz Mem0 gönderimini uzlaştır; otomatik tekrar yok')
            if previous and previous[1] and previous[2]=='ok':
                mark(r,'pending',previous[1])
                request('PUT','/v1/memories/'+previous[1]+'/',{'text':r['payload']['messages'][0]['content'],'metadata':r['payload']['metadata']})
                mark(r,'ok',previous[1])
                with brain.db() as con: con.execute('INSERT OR REPLACE INTO fingerprints VALUES (?,?,?)',('mem0',atom_hash,r['record']))
                continue
            # Persist BEFORE sending, so an interrupted process never blindly resubmits.
            mark(r,'pending')
            response=request('POST','/v3/memories/add/',r['payload'])
            results=response.get('results',[])
            if len(results)!=1 or not results[0].get('id'):
                mark(r,'reconcile-required',response.get('event_id','')); raise ValueError('Mem0 yanıtı eşleme için doğrulanamadı; yeniden ekleme yapılmadı')
            mark(r,'ok',str(results[0]['id']))
            with brain.db() as con: con.execute('INSERT OR REPLACE INTO fingerprints VALUES (?,?,?)',('mem0',atom_hash,r['record']))
    return len(batch)
def mem0_search(query):
    if brain.has_secret(query) or brain.is_sensitive(query): raise ValueError('Arama sorgusu gizlilik filtresine takıldı')
    # Only explicitly shareable queries may be supplied; do not derive from private notes.
    return request('POST','/v3/memories/search/',{'query':query[:300],'filters':{'user_id':brain.settings()['mem0']['user_id']},'top_k':5})
def mem0_smoke():
    text='RavenOS yapay bağlantı testi '+str(uuid.uuid4())
    if brain.has_secret(text) or brain.is_sensitive(text): raise ValueError('Yapay test filtresi başarısız')
    uid=str(uuid.uuid4()); rid=str(uuid.uuid4()); r={'service':'mem0','record':rid,'hash':brain.digest(text)}
    mark(r,'synthetic-pending')
    response=request('POST','/v3/memories/add/',{'user_id':uid,'infer':False,'messages':[{'role':'user','content':text}],'metadata':{'synthetic':True,'record_id':rid}})
    results=response.get('results',[])
    if len(results)!=1 or not results[0].get('id'): mark(r,'synthetic-reconcile',response.get('event_id','')); raise ValueError('Yapay kayıt kimliği doğrulanamadı')
    remote=str(results[0]['id']); mark(r,'synthetic-created',remote)
    try:
        found=request('POST','/v3/memories/search/',{'query':text,'filters':{'user_id':uid},'top_k':5})
        ok=any(str(x.get('id'))==remote for x in found.get('results',[]))
    finally:
        request('DELETE','/v1/memories/'+remote+'/'); mark(r,'deleted',remote)
    if not ok: raise ValueError('Arama doğrulanamadı; yapay kayıt silindi')
    brain.atomic(brain.STATE/'mem0-smoke.json',json.dumps({'status':'ok','time':brain.now()}))
    return {'add':'ok','search':'ok','delete':'ok'}
def claim(path):
    r=brain.export_record(path,'todoist')
    with brain.lock('todoist-outbox'):
        previous=state(r)
        if previous and previous[0]==r['hash'] and previous[2]=='ok': return {'status':'duplicate-skipped','record':r['record'],'remote':previous[1]}
        if previous and previous[2] not in ('ok','deleted'): raise ValueError('Belirsiz gönderim; önce Todoist içinde görev UUID’sini ara ve uzlaştır')
        payload=r['payload']; task={k:payload[k] for k in ('content','description','labels')}
        due=payload.get('due_string',payload.get('due_datetime',payload.get('due_date')))
        if due: task['dueString']=due
        conf=brain.settings()['todoist']
        if conf.get('project_id'): task['projectId']=conf['project_id']
        data,_,_=brain.parse_note(brain.safe_path(path))
        section=conf.get('sections',{}).get(data.get('area','personal'))
        if section: task['sectionId']=section
        mark(r,'claimed',previous[1] if previous else '')
        return {'status':'update' if previous and previous[1] else 'create','record':r['record'],'hash':r['hash'],'remote':previous[1] if previous else '', 'tasks':[task]}
def ack(rid,remote,content_hash):
    with brain.db() as con:
        row=con.execute('SELECT hash,status FROM sync WHERE service=? AND record=?',('todoist',rid)).fetchone()
        if not row or row[0]!=content_hash or row[1]!='claimed': raise ValueError('Eşleme makbuzu uyuşmuyor')
        con.execute('UPDATE sync SET remote=?,status=?,updated=? WHERE service=? AND record=?',(remote,'ok',brain.now(),'todoist',rid))
    brain.audit('sync',service='todoist',record=rid,status='ok')
    return {'status':'ok'}
def sync_all():
    if brain.settings()['mem0']['enabled']: mem0_sync()
    # OAuth connector only runs inside Codex; local scheduler never stores OAuth credentials.
    if brain.settings()['todoist']['enabled']: brain.audit('todoist-outbox',service='todoist',status='codex-connector-required',count=len(preview('todoist')['accepted']))
def main():
    p=argparse.ArgumentParser(); p.add_argument('command',choices=['preview','mem0-sync','mem0-test','todoist-claim','todoist-ack','mem0-forget']); p.add_argument('--service',choices=['mem0','todoist']); p.add_argument('--input'); p.add_argument('--record'); p.add_argument('--remote'); p.add_argument('--hash'); p.add_argument('--approve-delete',action='store_true'); a=p.parse_args()
    try:
        if a.command=='preview': result=preview(a.service)
        elif a.command=='mem0-sync': result=mem0_sync()
        elif a.command=='mem0-test': result=mem0_smoke()
        elif a.command=='todoist-claim': result=claim(a.input)
        elif a.command=='todoist-ack': result=ack(a.record,a.remote,a.hash)
        else:
            if not a.approve_delete: raise ValueError('Silme için açık onay gerekli')
            with brain.db() as con: row=con.execute('SELECT hash,remote,status FROM sync WHERE service=? AND record=?',('mem0',a.record)).fetchone()
            if not row or row[2]!='ok' or not row[1]: raise ValueError('Doğrulanmış eşleme bulunamadı')
            request('DELETE','/v1/memories/'+row[1]+'/'); mark({'service':'mem0','record':a.record,'hash':row[0]},'deleted',row[1]); result={'status':'deleted'}
        print(json.dumps(result,ensure_ascii=False,indent=2))
    except ValueError as e: print(json.dumps({'status':'blocked','reason':str(e)},ensure_ascii=False)); sys.exit(2)
if __name__=='__main__': main()
