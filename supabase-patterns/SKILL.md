---
name: supabase-patterns
description: Supabase patterns and troubleshooting — RLS, Edge Functions, Storage, Realtime, CLI workflows, and Supabase Management API usage.
---

# Supabase Patterns

Quick reference for working with Supabase — RLS, Edge Functions, Storage, Realtime, CLI workflows, and the Management API. For general Postgres query/schema patterns, see the `postgres-patterns` skill; for cross-DB migration workflow, see `database-migrations`.

## When to Activate

- Writing or reviewing RLS policies
- Working with Supabase Edge Functions, Storage, or Realtime
- Running Supabase CLI commands or Management API calls
- Troubleshooting a Supabase-specific error (CLI, Management API, or client SDK)

## Management API / Tooling Gotchas

### PowerShell + Supabase SQL Payloads

When sending SQL through PowerShell to the Supabase Management API, do not `ConvertTo-Json` the raw SQL string/body in a way that changes the payload shape. Preserve the raw SQL payload behavior expected by the endpoint. If a request returns a 400 after PowerShell serialization, inspect the final request body before retrying.

## Related

- Skill: `postgres-patterns` — query optimization, indexing, schema design
- Skill: `database-migrations` — cross-DB/ORM migration workflow
- Agent: `database-reviewer` — full database review workflow
