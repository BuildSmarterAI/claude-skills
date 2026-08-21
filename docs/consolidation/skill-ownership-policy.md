# Skill Ownership Policy

> **A classification is not ownership.** A skill is `REPO_LOCAL` only when a real repository and a
> canonical path are named. This policy exists because 20 skills were marked "belongs to a product
> repo" while no repository contained any of them — the label satisfied every audit and enforced
> nothing.

## The rule

```
REPO_LOCAL requires owner_repo AND owner_path.
An entry that names neither is not repo-local. It is unowned, and unowned means global.
```

Verify before classifying: a `<skill>/SKILL.md` must exist at `owner_path` on disk. Naming a
plausible repository is not evidence.

## Ownership classes

| Class | Meaning | Owner | Deployment |
|---|---|---|---|
| **GLOBAL-CANONICAL** | General capability, no product coupling | this repo | `IDENTICAL` to both runtimes |
| **SHARED-DOMAIN** | Domain knowledge spanning two or more products | this repo | `IDENTICAL`; never duplicated into each product repo |
| **AGENT-SUPPORTING-GLOBAL** | Backs an agent fleet — dispatches agents, or is dispatched by a skill that does | this repo | `IDENTICAL`; exposure follows the fleet's entry point |
| **GLOBAL-ON-DEMAND** | Global but rarely needed | this repo | `DISABLED` — source retained, exposed nowhere |
| **REPO-LOCAL** | Owned and maintained by one product repository | that repo | not deployed from here; `owner_repo` + `owner_path` mandatory |
| **VENDORED** | Imported from an upstream source | upstream | tracked, not locally edited |
| **ADAPTER** | Same capability, deliberately different per runtime | this repo | never cross-deployed — one copy would break the other |
| **DISABLED-PRESERVED** | Retired from exposure, byte-preserved | this repo + snapshot | staged out of the scanned root, never deleted |

## Deciding

1. **Does a repository already contain it?** → `REPO-LOCAL`. Record the verified path.
2. **Does its own description name exactly one product?** → `REPO-LOCAL` with that owner, but
   `DEFER_MOVE` unless the repo is healthy — recently committed, on its primary branch, and already
   carrying a skills directory.
3. **Does it name two or more products?** → `SHARED-DOMAIN`. One repo cannot own it, and copying it
   into each is how domain knowledge drifts apart.
4. **Do agents dispatch it, or does it dispatch agents?** → `AGENT-SUPPORTING-GLOBAL`. Establish the
   direction by reading the files; naming correspondence is not dependency. `audit-google` and
   `ads-google` sound coupled and are not — the audit agents are self-contained, and the dependency
   runs `ads` → agents.
5. **Otherwise** → `GLOBAL-CANONICAL`, or `GLOBAL-ON-DEMAND` if rarely needed.
6. **Cannot decide without a business call?** → `HUMAN-DECISION`. Never invent a repository.

## Ownership implies possession

If this repository owns a skill, this repository must **contain** it. D4.2 found 15 skills the
manifest claimed while canonical held no copy; they existed only in the runtime stores. Ownership
recorded against a source that lacks the file is the same defect as `REPO_LOCAL` with no repo.

## Exposure is a separate decision

Availability (which runtimes may have it) and exposure (whether its description is loaded every
turn) are independent. A skill can be `IDENTICAL` and `on-demand`. Never promote a skill to active
merely because it became available.

Before disabling anything, confirm nothing reaches it **by name**. A skill invoked by another skill
can be broken by an exposure change that discovery-based reasoning would call safe.

## Moving a skill

Classification changes freely; files move rarely. Prefer `DEFER_MOVE` and record `owner_repo`,
`owner_path`, dependencies, references that must change, and migration risk. A move is only
trivial when the target repo is healthy and nothing outside it references the skill.
