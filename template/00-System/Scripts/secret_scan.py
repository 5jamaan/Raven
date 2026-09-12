"""Pre-commit scan of staged bytes, not just the working directory."""
import subprocess,sys,json
import brain
def scan():
    names=subprocess.check_output(['git','diff','--cached','--name-only','--diff-filter=ACM','-z'],cwd=brain.ROOT).decode('utf-8').split('\0')
    bad=[];total=0
    for name in names:
        if not name: continue
        total+=1
        if name.startswith(('00-System/State/','00-System/Logs/')) or brain.Path(name).name.startswith('.env'):
            bad.append('Yasak çalışma dosyası: '+name);continue
        raw=subprocess.check_output(['git','show',':'+name],cwd=brain.ROOT)
        if b'\0' in raw:
            bad.append('İkili dosya manuel güvenlik incelemesi gerekli: '+name);continue
        content=raw.decode('utf-8',errors='replace')
        # Only the exact public policy digest is metadata, not a credential.
        if name == '00-System/Config/settings.json':
            try:
                config=json.loads(content)
                if config.get('mem0',{}).get('policy_approval') == brain.policy_hash():
                    config['mem0']['policy_approval']='verified-public-policy-digest'
                    content=json.dumps(config,ensure_ascii=False)
            except (ValueError,TypeError,AttributeError):
                pass
        if brain.has_secret(content):
            bad.append('Olası sır: '+name)
    if bad:
        print('\n'.join(bad));return 1
    print(str(total)+' sahnelenmiş dosya tarandı; tanımlı sır kalıpları bulunmadı.');return 0
if __name__=='__main__': sys.exit(scan())
