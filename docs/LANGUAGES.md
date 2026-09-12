# Languages and icons

Raven uses one codebase. English and Turkish are presentation choices, not separate products.

| Setting in `00-System/Config/settings.json` | Values | Meaning |
| --- | --- | --- |
| `language` | `en`, `tr` | Dashboard, templates, Base labels, generated memory headings |
| `conversation_language` | `auto`, `en`, `tr` | Agent response preference; explicit user requests take priority |
| `summary_language` | `en`, `tr` | Language requested for future summaries and topic labels |

New installations default to an English interface, automatic conversation language, and English summaries. Existing configurations without language keys retain Turkish runtime defaults. The installer never upgrades or modifies an existing vault.

Run `python 00-System/Scripts/localization.py --ui tr` from the installed vault to switch presentation. Add `--conversation en` or `--summary tr` independently. This is a local command, not an Obsidian plugin or an in-page language button. Editing the setting alone changes future runtime output but does not regenerate starter pages; use the command for a complete starter-page switch.

The command checks every tracked starter file before writing. An edited file aborts the switch without changes. Backups live outside the vault, under its runtime directory in `LocalizationBackups`. Reconcile edited starter pages before switching. Do not bypass the manifest to force an upgrade of a personal installation. Close other writers during the switch; the backup and rollback protect against ordinary write failures, not simultaneous edits or a power failure.

Personal notes, existing summaries, and source quotations are never translated. Future published memory pages receive translated headings around unchanged stored content. Paths, note IDs, metadata, statuses, filter expressions, task identities, and external service labels remain stable. Agent language preference is delivered at session start; open a new session after changing it. Language selection never enables processing or external integrations.

Catalogs are `00-System/Locales/en.json` and `tr.json`. Translation applies only to explicit literal messages and owned starter bodies. Never perform global replacement on notes or evidence. Internal diagnostic codes and integration payloads retain stable values.

## Desktop assets

`00-System/Assets/raven-terminal.ico` is the blue raven for the Raven terminal. `raven-dashboard.ico` is the purple symbol for the RavenOS Dashboard. User-supplied image bytes are preserved; descriptive package names replace historical naming.

Run `tools/create-shortcuts.ps1 -Vault <installed-vault>` from the source repository. The terminal shortcut opens native Codex with that vault as its working directory. The Dashboard shortcut opens `Dashboard.md` through Obsidian's URI handler. It does not install applications or approve hooks.

Names include the vault folder name so installations are distinguishable. Existing shortcuts are never overwritten. Optional `-Destination` creates them in another existing folder for inspection. Icons are included under the repository's MIT license.
