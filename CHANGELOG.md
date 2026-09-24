# Changelog

## 2026-09-24 — Filesystem and backup reliability

- Prune temporary folders, dependencies and caches before scanning. Reject symlinks and Windows junctions in explicit vault paths as well as scans and backups.
- Treat only the revision component of a canonical GitHub commit/tree/blob URL as source metadata. Credential assignments, bare hexadecimal values and other URL components remain screened.
- Publish backup ZIPs only after validation; clean up failed attempts and keep a consistent SQLite snapshot.
- Include filtering helpers in the privacy-policy fingerprint, requiring renewed Mem0 approval after this update.
- Preserve per-vault runtime isolation and both interface languages. No account settings, personal notes or runtime history are included.


## English / Turkish presentation and desktop assets

- English README with a Turkish companion document.
- Independent interface, conversation, and future-summary language preferences.
- Localized Dashboard, starter templates, Base labels, and generated memory presentation.
- Conservative language switching with edit detection, backups, and rollback; personal content and identifiers are preserved.
- User-supplied terminal and Dashboard icons, plus optional Windows shortcut creation without overwriting existing shortcuts.
- Existing personal vaults are not automatically migrated.

## 0.2.0 — initial public distribution

- Shared event capture for local Codex and Claude Code workspaces.
- Bounded background extraction with source quotes and per-project retrieval.
- Opt-out/read-only controls, source access checks and guarded generated-note updates.
- Blank vault templates, explicit cloud opt-in, new-folder installer and isolated runtime paths.
- Windows tests and a publication check to keep personal state out of the repository.

This is an early public release. It is not an automatic upgrade for existing private installations or a collector for all ordinary web chats.
