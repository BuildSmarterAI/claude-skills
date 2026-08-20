---
name: code-review
description: >
  Code review, debugging, and quality patterns. Use this skill when the user asks
  you to review code, find bugs, debug issues, audit security, optimize performance,
  or improve code quality. Also trigger when the user pastes code and asks "what's
  wrong" or "can you review this" or "why isn't this working" or describes unexpected
  behavior. Useful for finding common pitfalls in TypeScript, React, SQL, and API code.
---

# Code Review & Debugging

## Review Checklist

When reviewing code, check these in order:

### 1. Correctness
- Does it do what it's supposed to do?
- Are edge cases handled (null, empty, undefined, zero)?
- Are error paths handled properly?
- Do async operations have proper error handling?

### 2. Security
- SQL injection: Are queries parameterized?
- Auth: Is the user authenticated and authorized?
- Input validation: Is user input sanitized?
- Secrets: Any API keys, tokens, or passwords hardcoded?
- CORS: Are headers properly configured?
- RLS: Are database policies in place?

### 3. Performance
- N+1 queries: Is data fetched in loops?
- Missing indexes: Are filtered/joined columns indexed?
- Unnecessary re-renders: Are React dependencies correct?
- Large payloads: Is data over-fetched?
- Memory leaks: Are subscriptions/listeners cleaned up?

### 4. Maintainability
- Naming: Are variables/functions descriptive?
- Complexity: Can any function be simplified?
- Duplication: Is logic repeated that should be extracted?
- Types: Are TypeScript types specific (not `any`)?
- Comments: Is complex logic explained?

## Common Bug Patterns

### React
```tsx
// BUG: Stale closure
useEffect(() => {
  const interval = setInterval(() => {
    setCount(count + 1);  // 'count' is stale
  }, 1000);
  return () => clearInterval(interval);
}, []); // missing 'count' dependency

// FIX: Use functional update
setCount(prev => prev + 1);
```

```tsx
// BUG: Object/array in dependency array
useEffect(() => {
  fetchData(filters);
}, [filters]); // new object every render = infinite loop

// FIX: Memoize or use primitive values
const filterKey = JSON.stringify(filters);
useEffect(() => { fetchData(filters); }, [filterKey]);
```

### TypeScript
```typescript
// BUG: Optional chaining without null check
const name = user?.profile?.name;
console.log(name.toUpperCase()); // crash if undefined

// FIX:
console.log(name?.toUpperCase() ?? 'Unknown');
```

### SQL / Supabase
```sql
-- BUG: Missing org isolation
SELECT * FROM bids WHERE project_id = $1;

-- FIX: Always scope to organization
SELECT * FROM bids WHERE project_id = $1 AND organization_id = $2;
```

```typescript
// BUG: Not handling Supabase error
const { data } = await supabase.from('bids').select('*');
// 'data' could be null if error occurred

// FIX: Always check error
const { data, error } = await supabase.from('bids').select('*');
if (error) throw error;
```

### Async/Await
```typescript
// BUG: Sequential when could be parallel
const users = await fetchUsers();
const projects = await fetchProjects();

// FIX: Parallel execution
const [users, projects] = await Promise.all([
  fetchUsers(),
  fetchProjects()
]);
```

## Debugging Approach

1. **Reproduce** — Can you reliably trigger the bug?
2. **Isolate** — What's the smallest input that causes it?
3. **Trace** — Follow the data flow from input to unexpected output
4. **Hypothesize** — What could cause this specific behavior?
5. **Verify** — Add logging/breakpoints at the suspected point
6. **Fix** — Make the smallest change that fixes the issue
7. **Prevent** — Add a test that catches this regression

## Performance Profiling Questions
- Is the bottleneck in the query, the network, or the render?
- Is this O(n) or O(n²)? What's n at scale?
- Are you fetching data you don't display?
- Can this be cached? At what layer?
- Is this running on every render or only when data changes?
