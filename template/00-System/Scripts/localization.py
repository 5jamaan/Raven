"""Switch owned presentation files without translating personal notes or changing identifiers."""
import argparse
import hashlib
import json
import zipfile
import uuid
from pathlib import Path
import brain
from i18n import LANGUAGES, catalog

MANIFEST = '00-System/Config/localization-state.json'


def digest(data):
    return hashlib.sha256(data).hexdigest()


def outputs(language):
    result = {}
    data = catalog(language)
    for relative, body in data['documents'].items():
        path = brain.safe_path(relative)
        original = path.read_text(encoding='utf-8')
        # Preserve the complete original frontmatter, including note IDs and privacy.
        prefix = original.split('---\n', 2)
        if len(prefix) != 3 or prefix[0]:
            raise ValueError('Invalid starter frontmatter: '+relative)
        result[relative] = ('---\n'+prefix[1]+'---\n'+body).encode('utf-8')
    for relative, labels in data['bases'].items():
        value = json.loads(brain.safe_path(relative).read_text(encoding='utf-8'))
        for key, label in labels['properties'].items():
            value['properties'][key]['displayName'] = label
        for view, name in zip(value['views'], labels['views'], strict=True):
            view['name'] = name
        result[relative] = (json.dumps(value, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    return result


def change(language=None, conversation=None, summary=None, initialize=False):
    for value, allowed in ((language, LANGUAGES), (conversation, ('auto', *LANGUAGES)), (summary, LANGUAGES)):
        if value is not None and value not in allowed:
            raise ValueError('Unsupported language')
    conf = brain.settings()
    target = brain.safe_path(MANIFEST)
    updates = {}
    if language is not None:
        updates = outputs(language)
        if initialize:
            if target.exists():
                raise ValueError('Localization already initialized')
        else:
            if not target.exists():
                raise ValueError('No localization manifest. Use a new installation; existing vaults need a reviewed migration.')
            owned = json.loads(target.read_text(encoding='utf-8'))['files']
            if set(owned) != set(updates):
                raise ValueError('Localization file set changed; migration required')
            for relative, expected in owned.items():
                if digest(brain.safe_path(relative).read_bytes()) != expected:
                    raise ValueError('Edited presentation file; nothing changed: '+relative)
        conf['language'] = language
        updates[MANIFEST] = (json.dumps({'files': {p:digest(b) for p,b in updates.items()}}, indent=2)+'\n').encode('utf-8')
    if conversation is not None:
        conf['conversation_language'] = conversation
    if summary is not None:
        conf['summary_language'] = summary
    updates['00-System/Config/settings.json'] = (json.dumps(conf, ensure_ascii=False, indent=2)+'\n').encode('utf-8')
    # Full preflight precedes all writes. Back up outside the vault, and roll back I/O failures.
    previous = {p:brain.safe_path(p).read_bytes() if brain.safe_path(p).exists() else None for p in updates}
    backup = None
    if not initialize:
        folder = brain.runtime_dir()/'LocalizationBackups'
        folder.mkdir(parents=True, exist_ok=True)
        backup = folder/(str(uuid.uuid4())+'.zip')
        with zipfile.ZipFile(backup, 'x', zipfile.ZIP_DEFLATED) as archive:
            for p, data in previous.items():
                if data is not None:
                    archive.writestr(p, data)
    try:
        for p, data in updates.items():
            brain.atomic(brain.safe_path(p), data.decode('utf-8'))
    except Exception:
        for p, data in previous.items():
            if data is None:
                brain.safe_path(p).unlink(missing_ok=True)
            else:
                brain.atomic(brain.safe_path(p), data.decode('utf-8'))
        raise
    return backup


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ui', choices=LANGUAGES)
    parser.add_argument('--conversation', choices=('auto', *LANGUAGES))
    parser.add_argument('--summary', choices=LANGUAGES)
    args = parser.parse_args()
    if not any((args.ui, args.conversation, args.summary)):
        parser.error('Choose --ui, --conversation or --summary')
    try:
        backup = change(args.ui, args.conversation, args.summary)
    except (ValueError, OSError) as exc:
        parser.exit(1, str(exc)+'\n')
    print('Language settings updated. Backup: '+str(backup))
    print('New generated pages use the selected UI language; existing summaries and quotes retain their language.')


if __name__ == '__main__':
    main()
