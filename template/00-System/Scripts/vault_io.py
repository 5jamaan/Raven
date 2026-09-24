"""One filesystem boundary for vault scans, explicit paths and backups.

Directory links (including Windows junctions/reparse points) are never traversed.
This protects ordinary vault operations, not against a hostile process racing
filesystem changes with the same OS account.
"""
import os
import stat
from pathlib import Path

EXCLUDED = frozenset({'.git', '__pycache__', 'node_modules', 'tmp', 'temp',
                      '.venv', 'venv', '.cache', '.pytest_cache', '.mypy_cache'})


def is_link(path):
    info = path.lstat()
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, 'st_file_attributes', 0) & 0x400)


def safe_path(root, path):
    root = Path(os.path.abspath(root))
    canonical_root = root.resolve()
    raw = Path(path)
    # Inspect lexical ancestors BEFORE resolution, including internal links.
    candidate = Path(os.path.abspath(root / raw))
    try:
        parts = candidate.relative_to(root).parts
    except ValueError:
        # Windows can supply either a long path or its 8.3 spelling. Keep the
        # caller's root spelling so relative_to(ROOT) remains well-defined.
        try: parts = candidate.relative_to(canonical_root).parts
        except ValueError: raise ValueError('Vault dışı yol reddedildi') from None
    cursor = root
    for part in parts:
        if part.casefold() in EXCLUDED:
            raise ValueError('Geçici veya bağımlılık yolu reddedildi')
        cursor = cursor / part
        try:
            if is_link(cursor):
                raise ValueError('Bağlantılı dosya veya klasör reddedildi')
        except FileNotFoundError:
            pass
    if not cursor.resolve().is_relative_to(canonical_root):
        raise ValueError('Vault dışı yol reddedildi')
    return root.joinpath(*parts)


def files(root):
    """Prune before descending; propagate access/IO failures rather than hide them."""
    root = Path(os.path.abspath(root))
    def walk(folder):
        with os.scandir(folder) as entries:
            items = sorted(entries, key=lambda e: e.name.casefold())
        for entry in items:
            if entry.name.casefold() in EXCLUDED:
                continue
            path = Path(entry.path)
            if is_link(path):
                continue
            if entry.is_dir(follow_symlinks=False):
                yield from walk(path)
            elif entry.is_file(follow_symlinks=False):
                yield safe_path(root, path)
    yield from walk(root)
