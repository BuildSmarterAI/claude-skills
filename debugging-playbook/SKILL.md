---
name: debugging-playbook
description: Systematic debugging workflows for Supabase Edge Functions, Google Cloud Run services, RLS policy issues, PDF processing failures, and AI extraction pipeline errors. Use when troubleshooting production issues, investigating failures in ConstructIntel.ai or SiteIntel, or diagnosing performance problems.
---

# Debugging Playbook

Systematic investigation workflows for BuildSmarter production issues.

## When to Activate

- Debugging a production error or failure
- Investigating slow queries or timeouts
- Troubleshooting Edge Function or Cloud Run issues
- Diagnosing RLS policy problems (data not showing or leaking)
- Fixing PDF processing or AI extraction pipeline failures
- Investigating "it works locally but not in production"

## Triage: Where Is the Problem?

```
User reports issue
    │
    ├── UI not loading / blank page
    │   → Check Vercel deployment logs
    │   → Check browser console for JS errors
    │   → Check Supabase status (status.supabase.com)
    │
    ├── Data not showing / wrong data
    │   → RLS policy issue (most common)
    │   → Check auth.uid() matches expected user
    │   → Query the table with service_role to verify data exists
    │
    ├── API returning errors
    │   → Check Edge Function logs in Supabase dashboard
    │   → Check response status code and body
    │   → Verify env vars / secrets are set
    │
    ├── Processing job stuck / failed
    │   → Check processing_jobs table for status and error_message
    │   → Check Cloud Run logs in GCP console
    │   → Check if Cloud Run service is deployed and healthy
    │
    └── Slow performance
        → Check Supabase query performance (pg_stat_statements)
        → Check for missing indexes
        → Check Cloud Run cold start times
        → Check N+1 queries in frontend
```

## Supabase Edge Function Debugging

### Check Logs
```bash
# View recent function invocations
supabase functions logs process-document --limit 50

# Or in Supabase dashboard: Edge Functions → Logs
```

### Common Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 500 Internal Server Error | Unhandled exception | Add try/catch, check logs for stack trace |
| 401 Unauthorized | Missing or invalid JWT | Verify Authorization header passed from client |
| Function not found | Not deployed | `supabase functions deploy <name>` |
| Timeout | Processing too heavy | Offload to Cloud Run, keep Edge Function under 60s |
| Secret undefined | Secret not set | `supabase secrets set KEY=value` |
| CORS error | Missing headers | Add `Access-Control-Allow-Origin` to response |

### Debug Pattern

```typescript
// Add structured logging to Edge Functions
Deno.serve(async (req) => {
  const requestId = crypto.randomUUID();
  console.log(JSON.stringify({
    event: "request_received",
    requestId,
    method: req.method,
    url: req.url,
  }));

  try {
    const result = await processRequest(req);
    console.log(JSON.stringify({ event: "success", requestId }));
    return new Response(JSON.stringify({ data: result }), { status: 200 });
  } catch (err) {
    console.error(JSON.stringify({
      event: "error",
      requestId,
      error: err.message,
      stack: err.stack,
    }));
    return new Response(JSON.stringify({ error: { code: "internal_error" } }), { status: 500 });
  }
});
```

## Cloud Run Debugging

### Check Logs
```bash
# Recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=pdf-processor" --limit 50 --format json

# Or in GCP Console: Cloud Run → Service → Logs
```

### Common Failures

| Symptom | Likely Cause | Fix |
|---------|-------------|-----|
| 503 Service Unavailable | Cold start timeout | Set min-instances=1 for critical services |
| OOM killed (exit code 137) | Memory exceeded | Increase --memory (2Gi → 4Gi for PDF processing) |
| Timeout (504) | Processing too long | Increase --timeout, or chunk the work |
| Connection refused | Service not deployed | Check `gcloud run services list` |
| Secret not found | Secret Manager access | Grant service account `secretmanager.secretAccessor` role |
| Import error | Missing dependency | Check requirements.txt, rebuild container |

### Memory Debugging (PDF Processing)

```python
import tracemalloc
import psutil

tracemalloc.start()

# ... process PDF ...

current, peak = tracemalloc.get_traced_memory()
process = psutil.Process()
print(f"Current: {current / 1024 / 1024:.1f}MB, Peak: {peak / 1024 / 1024:.1f}MB")
print(f"RSS: {process.memory_info().rss / 1024 / 1024:.1f}MB")
tracemalloc.stop()
```

## RLS Policy Debugging

### "Data Not Showing" (Most Common Issue)

```sql
-- Step 1: Verify data exists (bypass RLS)
SET role TO service_role;
SELECT * FROM parcels WHERE id = 'parcel-uuid';
RESET role;

-- Step 2: Check what policies exist
SELECT * FROM pg_policies WHERE tablename = 'parcels';

-- Step 3: Test as the user
SET request.jwt.claims = '{"sub": "user-uuid", "role": "authenticated"}';
SELECT * FROM parcels WHERE id = 'parcel-uuid';
RESET request.jwt.claims;

-- Step 4: Check the policy USING clause
-- Common issue: auth.uid() doesn't match any row
SELECT auth.uid();  -- What does this return?
SELECT org_id FROM profiles WHERE id = 'user-uuid';  -- Does this match?
```

### "Data Leaking" (Security Issue)

```sql
-- Check if RLS is actually enabled
SELECT relname, relrowsecurity FROM pg_class WHERE relname = 'parcels';
-- relrowsecurity should be TRUE

-- Check for overly permissive policies
SELECT * FROM pg_policies WHERE tablename = 'parcels';
-- Look for policies with USING (true) or missing WHERE clauses

-- Test as anonymous (should return nothing for authenticated tables)
SET role TO anon;
SELECT * FROM parcels LIMIT 5;
RESET role;
```

## AI Extraction Pipeline Debugging

### Pipeline Stage Investigation

```
Job status: queued → processing → [FAILURE POINT] → completed

Check processing_jobs table:
```

```sql
SELECT id, status, error_message, error_details,
       created_at, updated_at,
       updated_at - created_at AS duration
FROM processing_jobs
WHERE id = 'job-uuid';
```

### Common Pipeline Failures

| Stage | Symptom | Fix |
|-------|---------|-----|
| PDF download | "File not found" or timeout | Check Supabase Storage URL, verify file exists |
| Text extraction | Empty text, garbled output | Check if PDF is scanned (needs OCR), check encoding |
| Classification | Wrong CSI division | Review classification prompt, add few-shot examples |
| LLM extraction | Timeout or rate limit | Implement retry with backoff, check API quota |
| LLM extraction | Hallucinated data | Add validation step, cross-reference with source text |
| Validation | Low confidence scores | Review extraction prompt, add structured output format |
| Result storage | DB write failure | Check RLS policies on results table, check data size |

### Isolate the Stage

```python
# Test each stage independently
# 1. Can we download the PDF?
text = extract_pdf_text(pdf_url)
print(f"Extracted {len(text)} chars from {pdf_url}")

# 2. Can we classify it?
classification = classify_document(text[:2000])
print(f"Classification: {classification}")

# 3. Can we extract with LLM?
result = call_llm_extraction(text, model="claude-haiku-4-5-20251001")
print(f"Extracted {len(result.get('line_items', []))} items")

# 4. Can we validate?
validated = validate_extraction(result)
print(f"Confidence: {validated['confidence']}")
```

## Performance Debugging

### Slow Supabase Queries

```sql
-- Find slow queries
SELECT query, mean_exec_time, calls, total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100
ORDER BY mean_exec_time DESC
LIMIT 10;

-- Check for missing indexes
EXPLAIN ANALYZE SELECT * FROM parcels WHERE county = 'harris';
-- If you see "Seq Scan" on a large table, add an index

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;
```

### Slow Frontend

```
1. Open browser DevTools → Network tab
2. Look for: 
   - Multiple sequential Supabase calls (N+1 → batch with .in() or joins)
   - Large payloads (SELECT * → select only needed columns)
   - Slow responses (>500ms → check query plan, add index)
3. React DevTools → Profiler
   - Look for unnecessary re-renders
   - Check if expensive components need React.memo
```

## Investigation Checklist

When a production issue is reported:

- [ ] **Reproduce:** Can you reproduce it? (specific user, specific input, specific time)
- [ ] **Isolate:** Which layer? (frontend, Edge Function, Cloud Run, database, external API)
- [ ] **Logs:** What do the logs say? (Supabase, Cloud Run, Vercel, browser console)
- [ ] **Recent changes:** Was anything deployed in the last 24 hours?
- [ ] **Scope:** Is it one user or all users? One operation or all operations?
- [ ] **Fix:** What's the minimal change to resolve it?
- [ ] **Verify:** Does the fix work in staging before production?
- [ ] **Prevent:** What test or monitoring would catch this next time?
