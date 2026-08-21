---
name: tech-docs
description: >
  Technical documentation, API docs, architecture decision records (ADRs), README files,
  runbooks, and developer guides. Use this skill when the user asks to write documentation,
  create a README, write an ADR, document an API, create a runbook, write a design doc,
  or produce any form of technical writing. Also trigger for changelog entries, release
  notes, onboarding guides, or internal wiki content.
---

# Technical Documentation Patterns

## README Structure

```markdown
# Project Name

One-line description of what this does.

## Quick Start
Minimal steps to get running (3-5 commands max).

## Prerequisites
What you need installed before starting.

## Installation
Step-by-step setup instructions.

## Usage
Core workflows with examples.

## Architecture
High-level system overview (can link to separate doc).

## Configuration
Environment variables and settings.

## Testing
How to run tests.

## Deployment
How to deploy.

## Contributing
How to contribute (branch strategy, PR process).

## License
```

## Architecture Decision Record (ADR)

```markdown
# ADR-NNN: Title of Decision

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**Deciders:** Names

## Context
What problem are we facing? What forces are at play?

## Decision
What did we decide to do?

## Consequences
What are the positive, negative, and neutral outcomes?

## Alternatives Considered
What else did we consider and why did we reject it?
```

## API Documentation

For each endpoint, document:
```markdown
### POST /api/bids

Create a new bid for a project.

**Auth:** Bearer token required. Requires `estimator` or `admin` role.

**Request Body:**
| Field | Type | Required | Description |
|-------|------|----------|-------------|
| project_id | UUID | Yes | Target project |
| subcontractor_id | UUID | Yes | Bidding subcontractor |
| base_amount | number | Yes | Total bid amount |
| legacy_division_id | UUID | Yes | CSI division |
| scope_type | string | No | "lump_sum" | "itemized" | "partial" |

**Response:** `201 Created`
```json
{
  "data": {
    "id": "uuid",
    "project_id": "uuid",
    "base_amount": 145000,
    "status": "received",
    "created_at": "2026-01-15T10:00:00Z"
  }
}
```

**Errors:**
| Code | Meaning |
|------|---------|
| 400 | Invalid input (missing required field, bad format) |
| 401 | Not authenticated |
| 403 | Not authorized for this organization |
| 404 | Project or subcontractor not found |
```

## Runbook Template

```markdown
# Runbook: [Incident Type]

## Symptoms
What does the user/system see when this happens?

## Severity
P1 (critical) / P2 (high) / P3 (medium) / P4 (low)

## Diagnosis Steps
1. Check [specific log/metric/dashboard]
2. Run [specific query/command]
3. Look for [specific pattern]

## Resolution Steps
1. Step-by-step fix instructions
2. Include exact commands
3. Note any rollback procedures

## Verification
How to confirm the fix worked.

## Prevention
What should be done to prevent recurrence.

## History
| Date | Occurrence | Resolution | Duration |
|------|-----------|------------|----------|
```

## Writing Principles

1. **Lead with the action** — "Run `npm install`" not "You should run `npm install`"
2. **Use present tense** — "The function returns" not "The function will return"
3. **Be specific** — "Set `MAX_RETRIES` to 3" not "Configure retries appropriately"
4. **Show, don't tell** — Include code examples for every concept
5. **Keep it scannable** — Use headers, tables, and code blocks liberally
6. **Assume intelligence, not knowledge** — Explain the "what" and "why," not just "how"
7. **Version your docs** — Include "Last Updated" dates
8. **Link, don't repeat** — Reference other docs instead of duplicating content
