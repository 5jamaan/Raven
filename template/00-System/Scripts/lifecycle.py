"""Stable Codex hook entry point. Raven v2 never forces an extra agent turn."""
from i18n import t
import json, sys
from raven_hook import handle
if __name__=='__main__':
    if hasattr(sys.stdin,'reconfigure'): sys.stdin.reconfigure(encoding='utf-8')
    if hasattr(sys.stdout,'reconfigure'): sys.stdout.reconfigure(encoding='utf-8')
    try: print(json.dumps(handle(json.load(sys.stdin),'codex'),ensure_ascii=False))
    except Exception:
        print(json.dumps({'systemMessage':t('Raven hafıza kaydı tamamlanamadı; hafıza durumunu kontrol et.')}))
