---
name: agent-eval
description: Head-to-head comparison of coding agents (Claude Code, Aider, Codex, etc.) on custom tasks with pass rate, cost, time, and consistency metrics
origin: ECC
tools: Read, Write, Edit, Bash, Grep, Glob
---

# Agent Eval Skill

A lightweight CLI tool for comparing coding agents head-to-head on reproducible tasks. Every "which coding agent is best?" comparison runs on vibes — this tool systematizes it.

## When to Activate

- Comparing coding agents (Claude Code, Aider, Codex, etc.) on your own codebase
- Measuring agent performance before adopting a new tool or model
- Running regression checks when an agent updates its model or tooling
- Producing data-backed agent selection decisions for a team

## Installation

> **Note:** Install agent-eval from its repository after reviewing the source.

## Core Concepts

### YAML Task Definitions

Define tasks declaratively. Each task specifies what to do, which files to touch, and how to judge success:

```yaml
name: add-retry-logic
description: Add exponential backoff retry to the HTTP client
repo: ./my-project
files:
  - src/http_client.py
prompt: |
  Add retry logic with exponential backoff to all HTTP requests.
  Max 3 retries. Initial delay 1s, max delay 30s.
judge:
  - type: pytest
    command: pytest tests/test_http_client.py -v
  - type: grep
    pattern: "exponential_backoff|retry"
    files: src/http_client.py
commit: "abc1234"  # pin to specific commit for reproducibility
```

### Git Worktree Isolation

Each agent run gets its own git worktree — no Docker required. This provides reproducibility isolation so agents cannot interfere with each other or corrupt the base repo.

### Metrics Collected

| Metric | What It Measures |
|--------|-----------------|
| Pass rate | Did the agent produce code that passes the judge? |
| Cost | API spend per task (when available) |
| Time | Wall-clock seconds to completion |
| Consistency | Pass rate across repeated runs (e.g., 3/3 = 100%) |

## Workflow

### 1. Define Tasks

Create a `tasks/` directory with YAML files, one per task:

```bash
mkdir tasks
# Write task definitions (see template above)
```

### 2. Run Agents

Execute agents against your tasks:

```bash
agent-eval run --task tasks/add-retry-logic.yaml --agent claude-code --agent aider --runs 3
```

Each run:
1. Creates a fresh git worktree from the specified commit
2. Hands the prompt to the agent
3. Runs the judge criteria
4. Records pass/fail, cost, and time

### 3. Compare Results

Generate a comparison report:

```bash
agent-eval report --format table
```

```
Task: add-retry-logic (3 runs each)
┌──────────────┬───────────┬────────┬────────┬─────────────┐
│ Agent        │ Pass Rate │ Cost   │ Time   │ Consistency │
├──────────────┼───────────┼────────┼────────┼─────────────┤
│ claude-code  │ 3/3       │ $0.12  │ 45s    │ 100%        │
│ aider        │ 2/3       │ $0.08  │ 38s    │  67%        │
└──────────────┴───────────┴────────┴────────┴─────────────┘
```

## Judge Types

### Code-Based (deterministic)

```yaml
judge:
  - type: pytest
    command: pytest tests/ -v
  - type: command
    command: npm run build
```

### Pattern-Based

```yaml
judge:
  - type: grep
    pattern: "class.*Retry"
    files: src/**/*.py
```

### Model-Based (LLM-as-judge)

```yaml
judge:
  - type: llm
    prompt: |
      Does this implementation correctly handle exponential backoff?
      Check for: max retries, increasing delays, jitter.
```

## Best Practices

- **Start with 3-5 tasks** that represent your real workload, not toy examples
- **Run at least 3 trials** per agent to capture variance — agents are non-deterministic
- **Pin the commit** in your task YAML so results are reproducible across days/weeks
- **Include at least one deterministic judge** (tests, build) per task — LLM judges add noise
- **Track cost alongside pass rate** — a 95% agent at 10x the cost may not be the right choice
- **Version your task definitions** — they are test fixtures, treat them as code

## Evaluation Methodology (EDD)

> Absorbed from the retired `eval-harness` skill. The above describes the tool; this section describes the methodology — eval-driven development (EDD), where you write evals BEFORE coding.

### pass@k vs pass^k

Two distinct success metrics for non-deterministic agents:

- **pass@k** — "at least one success in k attempts". pass@1 = first-attempt success rate. pass@3 = ≥1/3 attempts pass. Target: pass@3 > 90% for typical capability evals.
- **pass^k** — "all k trials succeed". pass^3 = three consecutive passes. Higher bar; use for critical paths (auth, payments, irreversible writes) where flaky-pass would ship a regression.

A 70% pass@1 agent has only 34% pass^3 (0.7³). Pick the metric that matches the cost of a wrong answer in production.

### EDD Workflow

1. **Define** (before coding):
   ```
   EVAL DEFINITION: feature-xyz
   Capability evals: [3-5 things this feature MUST do]
   Regression evals: [3-5 things that MUST keep working]
   Success metrics: pass@3 > 90% capability, pass^3 = 100% regression
   ```

2. **Implement** to pass the defined evals — no extra scope.

3. **Evaluate**: run capability + regression sets, record pass@k AND pass^k.

4. **Report**:
   ```
   Capability evals:  3/3 passed (pass@1=67%, pass@3=100%)
   Regression evals:  3/3 passed (pass^3=100%)
   Status: READY FOR REVIEW
   ```

### Where to Store Evals

Convention from eval-harness: `.claude/evals/<feature>/` containing:
- `definition.md` — the capability + regression lists with success metrics
- `runs/` — JSON results, one file per agent run, for trend analysis

This sits alongside the YAML task definitions used by the CLI above; the YAML drives execution, this folder records intent.

## Links

- Repository: [github.com/joaquinhuigomez/agent-eval](https://github.com/joaquinhuigomez/agent-eval)
