---
name: api-integration
description: >
  API design, REST patterns, OAuth flows, webhook handling, and third-party integration
  patterns. Use this skill when the user is building API endpoints, integrating with
  external APIs (Procore, Stripe, Google, etc.), implementing OAuth 2.0 flows, handling
  webhooks, designing request/response contracts, or dealing with rate limiting,
  pagination, or error handling for API calls.
---

# API Design & Integration Patterns

## REST Endpoint Design

```
GET    /api/resources          → List (with pagination, filtering)
GET    /api/resources/:id      → Get single resource
POST   /api/resources          → Create
PATCH  /api/resources/:id      → Partial update
DELETE /api/resources/:id      → Delete (prefer soft-delete)

# Nested resources
GET    /api/projects/:id/bids  → List bids for a project
POST   /api/projects/:id/bids  → Create bid under project
```

## Standard Response Format

```typescript
// Success
{
  "data": { ... },
  "meta": { "total": 100, "page": 1, "per_page": 25 }
}

// Error
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      { "field": "email", "message": "Invalid email format" }
    ]
  }
}
```

## Status Codes
- `200` OK — Successful GET/PATCH
- `201` Created — Successful POST
- `204` No Content — Successful DELETE
- `400` Bad Request — Invalid input
- `401` Unauthorized — Missing/invalid auth
- `403` Forbidden — Authenticated but not authorized
- `404` Not Found — Resource doesn't exist
- `409` Conflict — Duplicate/conflicting state
- `429` Too Many Requests — Rate limited
- `500` Internal Server Error — Unexpected failure

## OAuth 2.0 Authorization Code Flow

```
1. Redirect user to provider:
   GET https://provider.com/oauth/authorize?
     client_id=YOUR_ID&
     redirect_uri=YOUR_CALLBACK&
     response_type=code&
     scope=read+write&
     state=RANDOM_STATE

2. User authorizes → provider redirects to your callback:
   GET YOUR_CALLBACK?code=AUTH_CODE&state=RANDOM_STATE

3. Exchange code for tokens:
   POST https://provider.com/oauth/token
   {
     "grant_type": "authorization_code",
     "code": "AUTH_CODE",
     "client_id": "YOUR_ID",
     "client_secret": "YOUR_SECRET",
     "redirect_uri": "YOUR_CALLBACK"
   }
   → { "access_token": "...", "refresh_token": "...", "expires_in": 7200 }

4. Use access token:
   GET https://api.provider.com/resource
   Authorization: Bearer ACCESS_TOKEN

5. Refresh when expired:
   POST https://provider.com/oauth/token
   { "grant_type": "refresh_token", "refresh_token": "..." }
```

## Rate Limiting with Exponential Backoff

```typescript
async function fetchWithRetry(
  url: string,
  options: RequestInit,
  maxRetries = 3
): Promise<Response> {
  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    const response = await fetch(url, options);

    if (response.status === 429) {
      const retryAfter = response.headers.get('Retry-After');
      const delay = retryAfter
        ? parseInt(retryAfter) * 1000
        : Math.pow(2, attempt) * 1000 + Math.random() * 1000;

      console.log(`Rate limited. Retrying in ${delay}ms (attempt ${attempt + 1})`);
      await new Promise(resolve => setTimeout(resolve, delay));
      continue;
    }

    return response;
  }

  throw new Error(`Failed after ${maxRetries} retries`);
}
```

## Pagination Pattern

```typescript
async function fetchAllPages<T>(
  baseUrl: string,
  headers: Record<string, string>
): Promise<T[]> {
  const allItems: T[] = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const url = `${baseUrl}?page=${page}&per_page=100`;
    const response = await fetchWithRetry(url, { headers });
    const data = await response.json();

    allItems.push(...data.items);
    hasMore = data.items.length === 100;
    page++;
  }

  return allItems;
}
```

## Webhook Handling

```typescript
// Verify webhook signature
function verifyWebhookSignature(
  payload: string,
  signature: string,
  secret: string
): boolean {
  const hmac = crypto.createHmac('sha256', secret);
  const digest = hmac.update(payload).digest('hex');
  return crypto.timingSafeEqual(
    Buffer.from(signature),
    Buffer.from(`sha256=${digest}`)
  );
}

// Idempotent webhook processing
async function handleWebhook(event: WebhookEvent) {
  // Check if already processed
  const existing = await db.webhookLog.findUnique({
    where: { event_id: event.id }
  });
  if (existing) return { status: 'already_processed' };

  // Process
  await processEvent(event);

  // Log
  await db.webhookLog.create({
    data: { event_id: event.id, processed_at: new Date() }
  });
}
```

## Security Checklist for API Integrations
- [ ] Store tokens encrypted at rest
- [ ] Never log access tokens or secrets
- [ ] Validate webhook signatures before processing
- [ ] Use state parameter in OAuth to prevent CSRF
- [ ] Implement token refresh before expiry
- [ ] Rate limit your own outgoing requests
- [ ] Set timeouts on all external HTTP calls
- [ ] Handle provider downtime gracefully
