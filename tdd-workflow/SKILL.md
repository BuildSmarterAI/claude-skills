---
name: tdd-workflow
description: Use when writing or fixing TypeScript/Vitest/Playwright tests and you need the stack-specific patterns — unit vs integration vs E2E layout, Vitest ESM mocking, Testing Library queries, Playwright flake avoidance, coverage commands. Covers HOW to write the tests, not WHEN they must be written.
origin: ECC
---

# Test-Driven Development Workflow (TypeScript / Vitest / Playwright)

> **Testing ORDER is governed by `risk-based-tdd` — the canonical doctrine. Do not redefine it here.**
> That document decides *whether* tests must come first for a given change. This skill covers *how*
> to write them well on the TypeScript / Vitest / Playwright stack, once that decision is made.

For the generic RED-GREEN-REFACTOR execution loop, see `superpowers:test-driven-development`.

## When to Activate

- Writing new features or functionality in the TS/Next.js app
- Fixing bugs in API routes, components, or services
- Refactoring existing TypeScript code
- Adding Next.js API endpoints
- Creating new React components

## Stack-Specific Test Types

- **Unit (Vitest/Jest + Testing Library)** — components, hooks, pure utilities, helpers
- **Integration (Vitest + NextRequest)** — API route handlers, DB calls, service interactions
- **E2E (Playwright)** — critical user flows, browser automation, UI interactions

## Unit Test Pattern (Vitest + Testing Library)

```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'

describe('Button Component', () => {
  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByText('Click me')).toBeInTheDocument()
  })

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn()
    render(<Button onClick={handleClick}>Click</Button>)

    fireEvent.click(screen.getByRole('button'))

    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it('is disabled when disabled prop is true', () => {
    render(<Button disabled>Click</Button>)
    expect(screen.getByRole('button')).toBeDisabled()
  })
})
```

## Next.js API Route Integration Test

```typescript
import { NextRequest } from 'next/server'
import { GET } from './route'

describe('GET /api/markets', () => {
  it('returns markets successfully', async () => {
    const request = new NextRequest('http://localhost/api/markets')
    const response = await GET(request)
    const data = await response.json()

    expect(response.status).toBe(200)
    expect(data.success).toBe(true)
    expect(Array.isArray(data.data)).toBe(true)
  })

  it('validates query parameters', async () => {
    const request = new NextRequest('http://localhost/api/markets?limit=invalid')
    const response = await GET(request)

    expect(response.status).toBe(400)
  })

  it('handles database errors gracefully', async () => {
    // Mock database failure, then call GET and assert error shape
    const request = new NextRequest('http://localhost/api/markets')
    // Test error handling
  })
})
```

## Playwright E2E Recipes

```typescript
import { test, expect } from '@playwright/test'

test('user can search and filter markets', async ({ page }) => {
  await page.goto('/')
  await page.click('a[href="/markets"]')

  await expect(page.locator('h1')).toContainText('Markets')

  await page.fill('input[placeholder="Search markets"]', 'election')

  // Wait for debounce and results
  await page.waitForTimeout(600)

  const results = page.locator('[data-testid="market-card"]')
  await expect(results).toHaveCount(5, { timeout: 5000 })

  const firstResult = results.first()
  await expect(firstResult).toContainText('election', { ignoreCase: true })

  await page.click('button:has-text("Active")')
  await expect(results).toHaveCount(3)
})

test('user can create a new market', async ({ page }) => {
  await page.goto('/creator-dashboard')

  await page.fill('input[name="name"]', 'Test Market')
  await page.fill('textarea[name="description"]', 'Test description')
  await page.fill('input[name="endDate"]', '2025-12-31')

  await page.click('button[type="submit"]')

  await expect(page.locator('text=Market created successfully')).toBeVisible()
  await expect(page).toHaveURL(/\/markets\/test-market/)
})
```

## Test File Organization (Next.js App Router)

```
src/
├── components/
│   ├── Button/
│   │   ├── Button.tsx
│   │   ├── Button.test.tsx          # Unit tests (Vitest)
│   │   └── Button.stories.tsx       # Storybook
│   └── MarketCard/
│       ├── MarketCard.tsx
│       └── MarketCard.test.tsx
├── app/
│   └── api/
│       └── markets/
│           ├── route.ts
│           └── route.test.ts         # Integration tests
└── e2e/
    ├── markets.spec.ts               # Playwright E2E
    ├── trading.spec.ts
    └── auth.spec.ts
```

## Mocking External Services

### Supabase Mock

```typescript
jest.mock('@/lib/supabase', () => ({
  supabase: {
    from: jest.fn(() => ({
      select: jest.fn(() => ({
        eq: jest.fn(() => Promise.resolve({
          data: [{ id: 1, name: 'Test Market' }],
          error: null
        }))
      }))
    }))
  }
}))
```

### Redis Mock

```typescript
jest.mock('@/lib/redis', () => ({
  searchMarketsByVector: jest.fn(() => Promise.resolve([
    { slug: 'test-market', similarity_score: 0.95 }
  ])),
  checkRedisHealth: jest.fn(() => Promise.resolve({ connected: true }))
}))
```

### OpenAI Mock

```typescript
jest.mock('@/lib/openai', () => ({
  generateEmbedding: jest.fn(() => Promise.resolve(
    new Array(1536).fill(0.1) // Mock 1536-dim embedding
  ))
}))
```

## Vitest / Jest Coverage Config

```json
{
  "jest": {
    "coverageThresholds": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    }
  }
}
```

Run with `npm run test:coverage`. For Vitest, the equivalent lives under `test.coverage.thresholds` in `vitest.config.ts`.

## Stack-Specific Gotchas

### Prefer semantic / testid selectors in Playwright
CSS-hash classes (e.g. `.css-class-xyz`) break across Tailwind/Next.js builds. Use `button:has-text("Submit")` or `[data-testid="submit-button"]`.

### Test what the user sees in React, not internal state
Avoid `expect(component.state.count).toBe(5)` — Testing Library encourages `expect(screen.getByText('Count: 5')).toBeInTheDocument()`.

### Mocking ESM modules
When `package.json` has `"type": "module"` or you're using Vitest with ESM-published deps (Supabase JS, OpenAI SDK), prefer `vi.mock('@/lib/...', () => ({ ... }))` over `jest.mock`. Top-level `vi.mock` is hoisted; module-factory mocks must not reference outer variables.

### Next.js API route mocking
Use `NextRequest` from `next/server` directly — don't try to spin up a fake server. Call the exported `GET`/`POST` handler with the constructed `NextRequest` and assert against the returned `Response`.

### Playwright timing
Always pair UI actions that trigger debounced search (e.g. `page.fill` on a search input) with either `page.waitForTimeout(debounceMs)` or, better, `expect(locator).toHaveCount(...)` with a `timeout` option so the assertion polls.
