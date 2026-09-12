# Architecture

The public repository contains a vault template, not an active vault. The installer copies it into a new folder outside this checkout. It refuses existing targets and never installs or authenticates provider software.

`raven_hook.py` adapts Codex and Claude Code events. Codex supplies prompt/turn identifiers; Claude's missing turn identifier is matched against only the named session transcript under its known local projects directory. This is version-sensitive and fails closed when the latest prompt cannot be matched. Tool outputs and hidden reasoning are not collected.

`memory_engine.py` owns the local queue, project binding, provenance validation, generated notes, access filtering and opt-out state. SQLite lives in a per-vault namespace under the user's local application data. Different vaults must not silently share a queue. The memory worker uses an OS-held process lock and transactionally reserves the daily budget.

`memory_worker.py` batches new turns and invokes the explicitly configured subscription CLI in an isolated temporary directory with tools disabled. A worker-origin marker prevents recursive capture. Output quotes must appear verbatim in the corresponding user/assistant source. This proves quotation provenance, not truth or faithful interpretation of every summary sentence. Assistant proposals do not become confirmed user facts.

Session Markdown retains all accepted summaries. Project pages show a recent selection and possible common-topic links. Startup context retrieves a small, project-scoped selection. This is bounded lexical retrieval, not a complete semantic search engine. Long-lived session pages and the persistent index can still grow; the raw queue limit is not a full archival strategy.

The older `brain.py` and optional `gateway.py` retain note capture, review, privacy and export primitives. `session-close` is a legacy/manual operation; hooks never require a second model turn to run it. Mem0 and Todoist remain separate opt-in flows. A fresh install deliberately has no inherited live-test proof.

Changes made only for the public distribution include empty identities/configuration, explicit cloud opt-in, per-vault runtime isolation, generated local hooks, per-vault scheduler names and setup tests. They do not automatically migrate an existing personal Raven installation.
