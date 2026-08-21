---
name: risk-based-tdd
description: Use before writing any implementation, to decide whether tests must come first. The canonical BuildSmarter testing-order doctrine — test-first is mandatory for high-risk behaviour (business rules, parsers, state machines, security, authz, tenancy/RLS, spend, migrations, regression fixes, AI guardrails), optional for low-risk presentational and plumbing work. Also use when a bug fix needs a reproduction test, or when deciding whether mutation testing is required.
---

# Risk-Based TDD — the canonical testing-order doctrine

> **This is the single source of truth for WHEN tests are written at BuildSmarter.**
> Claude, Codex, repo agents, and skills all defer to this document.
> Do not restate or redefine testing order anywhere else — point here instead.

## 1. Principle

**Testing order is proportional to behavioural risk.**

Rigor is bought with effort, so spend it where a defect is expensive: silent, security-relevant,
irreversible, or hard to detect after the fact. Spend less where a defect is loud, visible, and cheap
to fix.

This is deliberately **not** "TDD everywhere" and deliberately **not** "tests whenever convenient".

## 2. Test-first is MANDATORY for

Write the test before the implementation when a change touches any of these:

1. **Business rules** — scoring, eligibility, pricing, tiering, quotas
2. **Parsers, normalizers, classifiers** — anything that turns unstructured input into structured data
3. **State machines and state transitions** — status fields, lifecycles, workflow gates
4. **Security controls**
5. **Authentication**
6. **Authorization**
7. **RLS / tenancy boundaries**
8. **Input validation and trust boundaries** — anything crossing from untrusted to trusted
9. **Regression fixes** (see §5)
10. **Previously observed production bugs**
11. **Edge-case-heavy logic** — where the interesting behaviour lives in the corners
12. **Financial / spend / quota / rate-limit controls**
13. **Data transformations where silent corruption is possible**
14. **Migration invariants**
15. **API contracts with non-trivial behaviour**
16. **AI deterministic guardrails and evaluators** — gates, validators, scorers, judges
17. **Any logic where mutation testing is appropriate** (see §6)

### Required loop for those categories

```
RED       write the test; run it; prove it fails FOR THE INTENDED REASON
   ↓      (a test that fails because of a typo or a missing import proves nothing)
GREEN     write the minimum implementation that satisfies it
   ↓
REFACTOR  improve the design without changing behaviour
   ↓
VERIFY    run the broader relevant test / verification surface
```

**"Prove it fails for the intended reason" is the load-bearing step.** Before writing the
implementation, name the production change that would make the test go green. If you cannot name it,
the test is not yet testing the thing you think it is.

## 3. Test-after is ACCEPTABLE for

Tests may follow the implementation for low-risk work:

- simple presentational UI
- styling
- copy changes
- static layout
- mechanical wiring
- trivial adapters
- configuration plumbing
- simple component composition
- generated boilerplate

**This is a relaxation of ordering, not of coverage.** The change still needs appropriate tests and
still must pass the repo's verification surface before it is called complete.

## 4. Decision rule

**When uncertain which category a change falls into, default to test-first.**

Classify **before** you implement, not after. "I'll decide once I see how it turns out" always
resolves to test-after, which is how the mandatory categories leak.

Some practical tie-breakers:

| Ask | If yes → test-first |
|---|---|
| Could this fail *silently*? | yes |
| Would a defect here be found by a human eyeballing the UI? | no → test-first |
| Does it decide who can see or do something? | yes |
| Does it spend money, consume quota, or contact a third party? | yes |
| Does it write to, or reshape, persisted data? | yes |
| Has something in this area broken in production before? | yes |

## 5. Regression rule

Every bug fix requires:

```
reproduction test FAILS   (demonstrating the bug)
   ↓
fix
   ↓
same test PASSES
```

The reproduction test must fail **against the unfixed code**. A test written after the fix, which has
never been seen red, does not establish that the bug is fixed — only that the code currently passes.

If a failure genuinely cannot be automated (external outage, hardware, a race that will not reproduce
in a harness), the agent must **explicitly document why** in the PR or commit body, and say what was
done instead. Silence is not an exemption.

## 6. Mutation-testing rule

For security controls, authorization, spend/ledger writes, destructive-action safeguards, and other
critical business gates:

**A passing test is insufficient evidence when mutation testing is practical.**

Deliberately break the implementation — one mutant at a time — and confirm the guarding test goes red.
A test that stays green against a broken implementation is not protecting anything.

Know the two failure modes and that they look identical (green suite, mutant applied):

- **weak test** — the test does not actually assert the guarded behaviour
- **bad mutant** — the mutation never really applied, or changed nothing observable

Diagnose which one you have **before** editing the test in response to a survivor.

> Reference implementation: `maxx-sales-genius/.claude/skills/mutation-battery`. Its philosophy is
> canonical: *"A passing test proves nothing until it has failed against a deliberately broken
> implementation."*

## 7. Existing-code rule

Risk-based TDD governs **new changes**, not historical code purity.

Do not rewrite unrelated implementation, backfill tests across untouched modules, or refactor working
code merely to satisfy TDD ceremony. If you touch a high-risk behaviour, that behaviour gets the
treatment in §2 — its neighbours do not.

## 8. Prototype rule

Exploratory spikes may bypass strict ordering **only when explicitly marked**:

```
PROTOTYPE / NON-PRODUCTION
```

Mark it in the file header, the PR title, or the commit body — somewhere a reviewer cannot miss.

Productionizing a prototype requires the tests its risk class demands (§2), **before merge**. A
prototype that quietly becomes production without that step is the single most common way mandatory
test-first work gets skipped.

## 9. AI-agent rule

Agents must **determine the risk class before implementation** and state it.

- For mandatory test-first work: **do not write production implementation first.** Not "write it then
  add the test", not "sketch it to see the shape". The test comes first.
- For low-risk work: implement freely, then cover and verify.
- State the classification explicitly, e.g. *"Risk class: authorization → test-first required."*
  A silent classification cannot be reviewed or challenged.

An agent that cannot decide the class must apply §4 and go test-first.

## 10. Tool integration — which TDD skill to invoke

The strict TDD skills available in this environment (`superpowers:test-driven-development`, and the
`tdd` / `tdd-workflow` capability skills) describe **how to execute** a rigorous red-green-refactor
loop. They are correct and should be used — but they do not decide *whether* the loop is mandatory.
This document does.

```
change classified HIGH-RISK (§2)
    → invoke strict TDD (superpowers:test-driven-development or equivalent)
    → follow RED → GREEN → REFACTOR → VERIFY
    → add mutation testing if §6 applies

change classified LOW-RISK (§3)
    → implement directly
    → cover the new behaviour with tests
    → run the repo's verification surface before claiming completion
    → do NOT invoke strict TDD purely by default
```

Two failure modes this ordering exists to prevent:

- **strict TDD applied by default to everything** — ceremony on a copy change, which trains people to
  route around the doctrine entirely
- **"implement first" applied by default to everything** — which is how an authorization gate ships
  with a test that has never been red

Neither tool silently wins. The **risk class decides**, and it is decided first.

## Repo-specific triggers

Repositories may declare additional domains that are **automatically** high-risk. Those lists live in
the repository, next to the code they describe — they extend §2 and never replace it:

- `maxx-sales-genius` → `AGENTS.md` § Testing-order policy
- `preconintel` → `CLAUDE.md` § Testing-order policy

## Anti-patterns

- ❌ Deciding the risk class after the implementation exists.
- ❌ Writing the reproduction test after the fix, so it is never seen red.
- ❌ Treating "risk-based" as permission to defer tests indefinitely.
- ❌ Restating a different testing-order rule in a repo file, agent, or skill instead of pointing here.
- ❌ Shipping a `PROTOTYPE` unmarked, or productionizing one without its §2 tests.
- ❌ Accepting a green mutation run without checking whether the mutant actually applied.
