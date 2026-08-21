---
name: react-typescript-patterns
description: >
  React 18 + TypeScript + Tailwind CSS + shadcn/ui development patterns. Use this
  skill when building React components, creating custom hooks, writing TypeScript
  interfaces/types, styling with Tailwind, using shadcn/ui components, working with
  React Router, implementing forms with react-hook-form + zod, or managing server
  state with @tanstack/react-query. Trigger for any frontend work involving JSX/TSX,
  component architecture, state management, or UI development.
---

# React + TypeScript + Tailwind Patterns

## Component Structure

```tsx
// PascalCase filename matching component name
// MyComponent.tsx

import { useState, useCallback } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Loader2, Plus, Trash2 } from 'lucide-react';

interface MyComponentProps {
  title: string;
  items: Item[];
  onAction?: (id: string) => void;
}

export function MyComponent({ title, items, onAction }: MyComponentProps) {
  const [selected, setSelected] = useState<string | null>(null);

  if (!items.length) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-muted-foreground">
        <p>No items found</p>
      </div>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent className="space-y-2">
        {items.map(item => (
          <div key={item.id} className="flex items-center justify-between p-3 rounded-lg border">
            <span className="font-medium">{item.name}</span>
            <Button variant="ghost" size="sm" onClick={() => onAction?.(item.id)}>
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
```

## Custom Hook with React Query

```typescript
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';

// Fetch hook
export function useItems(filters?: { status?: string }) {
  return useQuery({
    queryKey: ['items', filters],
    queryFn: async () => {
      const response = await fetch(`/api/items?${new URLSearchParams(filters)}`);
      if (!response.ok) throw new Error('Failed to fetch');
      return response.json() as Promise<Item[]>;
    },
    staleTime: 5 * 60 * 1000,  // 5 minutes
  });
}

// Mutation hook
export function useCreateItem() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (input: CreateItemInput) => {
      const response = await fetch('/api/items', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(input),
      });
      if (!response.ok) throw new Error('Failed to create');
      return response.json() as Promise<Item>;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['items'] });
    },
  });
}
```

## Form with react-hook-form + zod

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from '@/components/ui/form';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const formSchema = z.object({
  name: z.string().min(1, 'Name is required'),
  email: z.string().email('Invalid email'),
  role: z.enum(['admin', 'editor', 'viewer']),
  amount: z.coerce.number().positive('Must be positive'),
});

type FormValues = z.infer<typeof formSchema>;

export function MyForm({ onSubmit }: { onSubmit: (data: FormValues) => void }) {
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: '', email: '', role: 'viewer', amount: 0 },
  });

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>Name</FormLabel>
              <FormControl>
                <Input placeholder="Enter name" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />
        <Button type="submit" disabled={form.formState.isSubmitting}>
          {form.formState.isSubmitting ? <Loader2 className="animate-spin mr-2 h-4 w-4" /> : null}
          Submit
        </Button>
      </form>
    </Form>
  );
}
```

## TypeScript Patterns

```typescript
// Discriminated union for status
type BidStatus = 'received' | 'reviewing' | 'selected' | 'rejected';

// Generic with constraints
interface DataTableProps<T extends { id: string }> {
  data: T[];
  columns: ColumnDef<T>[];
  onRowClick?: (item: T) => void;
}

// Utility types
type CreateInput = Omit<FullEntity, 'id' | 'created_at' | 'updated_at'>;
type UpdateInput = Partial<CreateInput> & { id: string };

// Exhaustive switch
function getStatusColor(status: BidStatus): string {
  switch (status) {
    case 'received': return 'bg-blue-100 text-blue-800';
    case 'reviewing': return 'bg-yellow-100 text-yellow-800';
    case 'selected': return 'bg-green-100 text-green-800';
    case 'rejected': return 'bg-red-100 text-red-800';
    default: {
      const _exhaustive: never = status;
      return 'bg-gray-100';
    }
  }
}
```

## Tailwind Patterns

```tsx
// Responsive grid
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">

// Conditional classes (use clsx or cn)
import { cn } from '@/lib/utils';
<div className={cn("p-4 rounded-lg border", isActive && "border-primary bg-primary/5")} />

// Common utility combos
"flex items-center justify-between"      // Horizontal layout
"flex flex-col gap-4"                     // Vertical stack
"text-sm text-muted-foreground"           // Secondary text
"truncate max-w-[200px]"                  // Overflow handling
"animate-spin h-4 w-4"                   // Loading spinner
```

## File Organization
```
src/
├── components/ui/       # shadcn/ui primitives (don't edit)
├── components/[domain]/ # Feature-specific components
├── hooks/               # Custom hooks (useX pattern)
├── pages/               # Route-level components
├── contexts/            # React contexts
├── types/               # Shared TypeScript types
├── lib/                 # Utilities (cn, formatters)
└── integrations/        # API client configuration
```
