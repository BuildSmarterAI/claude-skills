---
name: iterative-retrieval
description: Pattern for progressively refining context retrieval to solve the subagent context problem
origin: ECC
---

# Iterative Retrieval Pattern

Solves the "context problem" in multi-agent workflows where subagents don't know what context they need until they start working.

## When to Activate

- Spawning subagents that need codebase context they cannot predict upfront
- Building multi-agent workflows where context is progressively refined
- Encountering "context too large" or "missing context" failures in agent tasks
- Designing RAG-like retrieval pipelines for code exploration
- Optimizing token usage in agent orchestration

## The Problem

Subagents are spawned with limited context. They don't know:
- Which files contain relevant code
- What patterns exist in the codebase
- What terminology the project uses

Standard approaches fail:
- **Send everything**: Exceeds context limits
- **Send nothing**: Agent lacks critical information
- **Guess what's needed**: Often wrong

## The Solution: Iterative Retrieval

A 4-phase loop that progressively refines context using Claude Code's built-in tools:

```
┌─────────────────────────────────────────────┐
│                                             │
│   ┌──────────┐      ┌──────────┐            │
│   │ DISPATCH │─────▶│ EVALUATE │            │
│   └──────────┘      └──────────┘            │
│        ▲                  │                 │
│        │                  ▼                 │
│   ┌──────────┐      ┌──────────┐            │
│   │   LOOP   │◀─────│  REFINE  │            │
│   └──────────┘      └──────────┘            │
│                                             │
│        Max 3 cycles, then proceed           │
└─────────────────────────────────────────────┘
```

### Phase 1: DISPATCH

Start with the broadest signal-hunt that costs the fewest tokens. Pair a `Glob` for file shape with a `Grep` for terminology:

```
Glob("src/**/*.{ts,tsx,js}")
  → file inventory; note hot directories

Grep("authentication|session|user",
     glob="src/**/*.{ts,tsx,js}",
     output_mode="files_with_matches",
     head_limit=20)
  → small set of candidate files to inspect
```

Do not Read full files yet — you are only collecting candidates.

### Phase 2: EVALUATE

For each candidate, judge relevance against the task before committing more tokens:

```
For each candidate path from Phase 1:
  Grep("<task-specific term>", path=<file>, -A=3, -B=1, -n=true)
    → snippet view; is the match load-bearing or incidental?

  If snippet looks central:
    Read(<file>, offset=<match_line - 20>, limit=60)
    → confirm the surrounding logic actually implements the target
```

Scoring criteria (assign mentally, do not over-engineer):
- **High (0.8-1.0)**: Directly implements target functionality — keep in context
- **Medium (0.5-0.7)**: Related types, callers, or helpers — keep a reference
- **Low (0.2-0.4)**: Tangentially related — note path only
- **None (0-0.2)**: Not relevant — add to exclude list

### Phase 3: REFINE

Use what Phase 2 revealed to rewrite the next query. Three refinement moves:

1. **Adopt the codebase's vocabulary.** If you searched `rate limit` and only found `throttle`, switch terms.
2. **Narrow the path scope.** If 3 of 4 hot files live under `src/auth/`, scope the next `Grep` with `path="src/auth/"`.
3. **Target the gap.** If you have the middleware but not its caller, search for imports of the symbol you found.

```
Grep("import.*<symbol>|require.*<symbol>",
     glob="src/**/*.ts",
     output_mode="content",
     -n=true)
  → finds call sites; reveals where the bug is triggered, not just where it lives
```

### Phase 4: LOOP

Repeat with refined criteria. Stop conditions (whichever comes first):
- 3 high-relevance files identified AND no remaining critical gaps
- 3 cycles completed
- A subagent dispatch can answer the remaining question with what you have

When you need a focused second opinion without polluting your own context, dispatch a subagent:

```
Task(description="Verify <hypothesis>",
     prompt="Read <file>:<line-range>. Answer: <single sharp question>.
            Do not explore beyond the cited range unless the answer
            requires it. Return citations.")
```

## Practical Examples

### Example 1: Bug Fix Context

```
Task: "Fix the authentication token expiry bug"

Cycle 1 — broad signal hunt:
  Glob("src/**/*auth*.{ts,tsx,js}")
    → 12 candidate files
  Grep("validateToken|authenticate|verify",
       glob="src/**/*.ts",
       output_mode="files_with_matches")
    → 4 hot files: auth.ts, tokens.ts, middleware.ts, user.ts

Cycle 2 — narrow to the bug surface:
  Grep("session.*expir|token.*expir|exp.*claim",
       path="src/auth/",
       -A=10, -B=2, -n=true)
    → match cluster in middleware.ts:120-180 and tokens.ts:45-70
  Read("src/auth/middleware.ts", offset=110, limit=80)
    → confirms refresh path; user.ts is unrelated (drop it)

Cycle 3 — refine with subagent:
  Task(description="Verify session expiry refresh logic",
       prompt="Read src/auth/middleware.ts:120-180 and
              src/auth/tokens.ts:45-70. Does the refresh path
              correctly extend the JWT exp claim, or does it just
              create a new session entry without expiring the old?
              Cite line numbers.")
    → subagent reports: new session created, old not invalidated

Result: auth.ts, tokens.ts, middleware.ts:120-180 — bug localized
        without ever loading user.ts or full middleware.ts into context
```

### Example 2: Feature Implementation

```
Task: "Add rate limiting to API endpoints"

Cycle 1 — broad signal hunt:
  Grep("rate.?limit|RateLimit",
       glob="src/**/*.ts",
       output_mode="files_with_matches")
    → 0 matches; the codebase does not use this term

Cycle 2 — adopt local vocabulary:
  Glob("src/middleware/**/*.ts")
    → 8 middleware files
  Grep("throttle|debounce|quota|bucket",
       glob="src/**/*.ts",
       output_mode="files_with_matches")
    → throttle.ts, middleware/index.ts — terminology is "throttle"

Cycle 3 — find the wiring:
  Read("src/middleware/throttle.ts")  -- small file, read whole
  Grep("app\\.use|router\\.use|registerMiddleware",
       glob="src/**/*.ts",
       -A=3, -n=true)
    → router-setup.ts:42 registers middleware chain

Result: throttle.ts (pattern to follow), middleware/index.ts
        (registration point), router-setup.ts:42 (insertion site)
```

## Integration with Subagent Prompts

When delegating retrieval to a subagent, give it the loop as instructions:

```markdown
You are retrieving context for: <task>

Run up to 3 cycles:

1. DISPATCH — broad Glob + Grep with task keywords. Do not Read yet.
2. EVALUATE — Grep each candidate with -A/-B for snippet context.
   Read only when a snippet looks central, and pass offset+limit
   to avoid loading the whole file.
3. REFINE — adopt codebase vocabulary, narrow path scope, target gaps.
4. STOP when you have 3 high-relevance files and no critical gaps,
   or after 3 cycles.

Return: file paths with line ranges and a one-line relevance note each.
```

## Best Practices

1. **Start broad, narrow progressively** — first `Grep` should use `output_mode="files_with_matches"`, never `content`
2. **Learn codebase terminology before reading** — Cycle 1 often reveals the project says `throttle` not `rate limit`
3. **Use `offset` + `limit` on `Read`** — load 60 lines around a hit, not the whole 800-line file
4. **Track what's missing explicitly** — write the gap as a sentence before forming the next query
5. **Stop at "good enough"** — 3 high-relevance files beats 10 mediocre ones
6. **Dispatch subagents for verification, not exploration** — give them a sharp question and a cited range

## Related

- `superpowers:dispatching-parallel-agents` — when retrieval branches are independent
- `superpowers:systematic-debugging` — pairs well with iterative retrieval during bug hunts
- `continuous-learning-v2` skill — for patterns that improve over time
- Agent definitions in `~/.claude/agents/`
