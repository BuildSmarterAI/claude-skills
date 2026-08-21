# Divergence Adjudication — Claude runtime vs Codex runtime

**65 shared skills differ between the two runtime stores.**

## Root cause (confirmed, not inferred)

The Codex store was produced by a **blind `Claude` → `Codex` string substitution**.
The evidence is unambiguous — the substitution hit content it should never have touched:

| Damage | Occurrences |
|---|---:|
| Broken paths `~/.Codex/...` | 72 |
| Broken paths `.Codex/...` | 28 |
| Frontmatter `name:` mangled (`Codex-api`, `Codex-devfleet`, `Codex-handoff`, `git-guardrails-Codex`) | 4 |
| Nonexistent product "Codex Desktop" | 2 |
| Nonsense `Codex, Cursor, Codex` (was `Claude Code, Cursor, Codex`) | 2 |
| Broken MCP name `Codex-in-chrome` | 1 |

**31 of 65 divergent skills contain at least one such defect.** Separately, **6 Codex
skills lost their entire YAML frontmatter** (`benchmark`, `browser-qa`, `canary-watch`,
`design-system`, `product-lens`, `safety-guard`) — a `SKILL.md` starting with a bare `#`
is never registered, so those six are silently invisible to Codex.

Structural defects: **Codex store 11, Claude store 0.**

## Adjudication rule

For every divergent skill except one, the **Claude side is canonical** — it carries zero
structural defects, and the canonical repo already matched the Claude side in 21 cases and
the Codex side in **0**. The symmetric unique-line counts (11/11, 30/30, 58/58 …) are the
signature of a substitution rather than independent authorship.

## The one genuine exception

`code-review` is **not** one skill that drifted — it is **two different capabilities sharing
a name** (shared-line ratio **0.019**):

- **Claude variant** — "Code Review & Debugging": a quality checklist (correctness, security,
  performance, maintainability) plus React/TypeScript/SQL bug patterns.
- **Codex variant** — a **dual-axis reviewer**: Standards (repo coding standards + a Fowler
  code-smell baseline) and Spec (does the diff match the originating issue/PRD?), run as
  **parallel sub-agents** and reported side by side without cross-axis reranking.

> The earlier infrastructure audit listed *"dual-axis review — a spec-compliance reviewer
> distinct from the quality reviewer"* as one of only three **truly missing** capabilities in
> the entire fleet. It was never missing — it existed in the Codex store only, invisible to
> Claude. Both variants are preserved; which one keeps the bare name `code-review` is a
> **human decision** (it changes dispatch for a heavily-used capability).

## Major divergences (>20 changed lines)

| Skill | diff lines | shared ratio | Claude bytes | Codex bytes | Decision |
|---|---:|---:|---:|---:|---|
| `code-review` | 155 | 0.019 | 3911 | 6740 | PRESERVE BOTH (human naming decision) |
| `autonomous-loops` | 120 | 0.842 | 25336 | 25247 | Claude side canonical |
| `configure-ecc` | 64 | 0.86 | 16135 | 16029 | Claude side canonical |
| `claude-api` | 50 | 0.901 | 8881 | 8854 | Claude side canonical |
| `skill-stocktake` | 41 | 0.825 | 8001 | 7960 | Claude side canonical |
| `codebase-onboarding` | 36 | 0.888 | 8456 | 8438 | Claude side canonical |
| `continuous-learning-v2` | 28 | 0.94 | 12913 | 12889 | Claude side canonical |
| `git-guardrails-claude-code` | 22 | 0.686 | 2312 | 2284 | Claude side canonical |
| `context-budget` | 22 | 0.878 | 5825 | 5812 | Claude side canonical |
| `security-scan` | 22 | 0.882 | 4634 | 4605 | Claude side canonical |
| `plankton-code-quality` | 22 | 0.941 | 8186 | 8154 | Claude side canonical |

## Remaining 54 divergences

36 trivial (≤4 significant lines) and 18 minor (5–20) — all attributable to the same
substitution plus small edits. Resolution: **Claude side canonical**, normalising line
endings automatically. None requires human input.

