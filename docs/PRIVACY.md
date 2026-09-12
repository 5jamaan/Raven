# Privacy and data boundaries

- Public source contains no personal records. Install outside the source repository. Do not publish your generated vault or its Git history.
- New installations disable capture, cloud processing, Mem0 and Todoist. Enabling cloud memory permits the selected provider to process the relevant captured source text, including text originating from the other provider.
- `private` means restricted by Raven's configured workflow; it does not mean that text read by a cloud assistant stays on the computer. `strict-local` blocks this worker's private cloud processing. These settings are not an operating-system sandbox for arbitrary agents or connectors.
- Known secret patterns are masked before the queue. Regex cannot recognize every secret or every natural-language opt-out. Use explicit controls for certainty.
- A paused/forgotten session is excluded from retrieval. Forgetting does not delete provider history, user copies or old backups. Successful extraction clears raw queue text; waiting text expires during the next maintenance pass after retention. An offline computer cannot perform expiry work.
- Source summaries are private, unverified and ineligible for Mem0 by default. A copied quote is not proof that the underlying claim is correct.
- Durable snapshots exclude raw queue contents and rotate through 31 daily slots. Manual ZIP backups are separate and may contain private notes. Windows Credential Manager entries are not shipped or copied into Git.
- Do not put secrets into bug reports. Report a redacted reproduction or code-level issue through the repository's private security reporting mechanism if the host offers one; otherwise request a private contact without publishing sensitive details.

See the installed vault's policies before opting into external integrations. Todoist's delivery and account-specific reminder capability require a real device test; a task due date alone is not proof of a delivered notification.
