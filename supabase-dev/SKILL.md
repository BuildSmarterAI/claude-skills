---
name: supabase-dev
description: >
  Supabase development patterns for PostgreSQL, Edge Functions, RLS policies, Auth,
  and Storage. Use this skill whenever the user is working with Supabase, writing
  PostgreSQL migrations, creating Edge Functions in Deno/TypeScript, configuring
  Row-Level Security policies, setting up authentication flows, or working with
  Supabase Storage buckets. Also trigger for any mentions of supabase-js client,
  Supabase CLI, database functions, triggers, materialized views, or RPC calls.
  Even if the user just says "write a migration" or "add RLS" without mentioning
  Supabase by name, use this skill.
---

# Supabase Development Patterns

## Migration Files

Always create migrations with timestamps and descriptive names:
```sql
-- File: supabase/migrations/YYYYMMDDHHMMSS_description.sql

-- Forward migration
CREATE TABLE new_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW(),
  deleted_at TIMESTAMPTZ,
  deleted_by UUID REFERENCES auth.users(id)
);

-- Enable RLS
ALTER TABLE new_table ENABLE ROW LEVEL SECURITY;

-- Create indexes
CREATE INDEX idx_new_table_org ON new_table(organization_id);

-- RLS Policies
CREATE POLICY "select_own_org" ON new_table
  FOR SELECT USING (organization_id = auth.jwt()->>'organization_id');

CREATE POLICY "insert_own_org" ON new_table
  FOR INSERT WITH CHECK (organization_id = auth.jwt()->>'organization_id');

-- Include rollback as comments
-- DROP TABLE IF EXISTS new_table;
```

## Edge Functions

Standard Edge Function structure:
```typescript
// supabase/functions/function-name/index.ts
import { serve } from 'https://deno.land/std@0.168.0/http/server.ts';
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2';

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
};

serve(async (req) => {
  // Handle CORS preflight
  if (req.method === 'OPTIONS') {
    return new Response(null, { headers: corsHeaders });
  }

  try {
    // Create admin client
    const supabase = createClient(
      Deno.env.get('SUPABASE_URL')!,
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
    );

    // Validate auth
    const authHeader = req.headers.get('Authorization');
    if (!authHeader) {
      return new Response(JSON.stringify({ error: 'Missing authorization' }), {
        status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    const { data: { user }, error: authError } = await supabase.auth.getUser(
      authHeader.replace('Bearer ', '')
    );
    if (authError || !user) {
      return new Response(JSON.stringify({ error: 'Invalid token' }), {
        status: 401, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
      });
    }

    // Parse request body
    const body = await req.json();

    // Your logic here...

    return new Response(JSON.stringify({ success: true }), {
      headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });

  } catch (error) {
    return new Response(JSON.stringify({ error: error.message }), {
      status: 500, headers: { ...corsHeaders, 'Content-Type': 'application/json' }
    });
  }
});
```

## RLS Policy Patterns

```sql
-- Viewer: read own org data
CREATE POLICY "viewers_select" ON table_name FOR SELECT
  USING (organization_id = (SELECT organization_id FROM profiles WHERE id = auth.uid()));

-- Editor: insert/update own org data
CREATE POLICY "editors_insert" ON table_name FOR INSERT
  WITH CHECK (
    organization_id = (SELECT organization_id FROM profiles WHERE id = auth.uid())
    AND (SELECT role FROM profiles WHERE id = auth.uid()) IN ('admin', 'editor')
  );

-- Admin only: delete
CREATE POLICY "admin_delete" ON table_name FOR DELETE
  USING (
    organization_id = (SELECT organization_id FROM profiles WHERE id = auth.uid())
    AND (SELECT role FROM profiles WHERE id = auth.uid()) = 'admin'
  );
```

## Database Functions (RPCs)

```sql
CREATE OR REPLACE FUNCTION get_data_for_org(p_organization_id UUID)
RETURNS SETOF table_name
LANGUAGE plpgsql
SECURITY DEFINER
SET search_path = public
AS $$
DECLARE
  v_user_org_id UUID;
BEGIN
  SELECT organization_id INTO v_user_org_id
  FROM profiles WHERE id = auth.uid();

  IF p_organization_id != v_user_org_id THEN
    RAISE EXCEPTION 'Access denied';
  END IF;

  RETURN QUERY SELECT * FROM table_name
  WHERE organization_id = p_organization_id;
END;
$$;
```

## Calling from Frontend

```typescript
// Direct query
const { data, error } = await supabase
  .from('table_name')
  .select('*, related:related_table(id, name)')
  .eq('organization_id', orgId)
  .order('created_at', { ascending: false });

// RPC call
const { data, error } = await supabase
  .rpc('function_name', { p_organization_id: orgId });

// Edge Function call
const { data, error } = await supabase.functions.invoke('function-name', {
  body: { key: 'value' }
});
```

## CLI Commands
```bash
supabase migration new description_here    # Create migration
supabase db push                           # Apply migrations
supabase functions serve function-name     # Local dev
supabase functions deploy function-name    # Deploy
supabase db reset                          # Reset local DB
supabase gen types typescript --local      # Regen TypeScript types
```
