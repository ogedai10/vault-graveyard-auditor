---
name: audit-vault
description: Use when the user wants to audit a markdown/Obsidian vault for "dead" notes — captures and summaries with no opinion of their own. Triggers on "audit my vault", "graveyard score", "how many of my notes are dead", "is my second brain a graveyard".
---

# Audit Vault

Runs the Vault Graveyard Auditor over a notes folder and reports how many notes are dead
captures vs notes carrying the user's own take.

## Steps
1. Ask for (or confirm) the vault path if not given.
2. From this repo's root, run:
   ```bash
   python -m vaultaudit <vault-path>
   ```
   Add `--llm` only if the user asks for a sharper pass and has `ANTHROPIC_API_KEY` set.
3. Read the printed `GRAVEYARD SCORE` and the worst offenders.
4. Tell the user the score plainly, name 3-5 worst notes, and for each say the one fix:
   add what THEY think about the source. The point is output, not storage.
5. The full table is in `graveyard-report.md`.
