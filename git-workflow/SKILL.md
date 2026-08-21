---
name: git-workflow
description: >
  Git workflow, branching strategy, commit message conventions, and PR best practices.
  Use this skill when the user asks about Git commands, branching, merging, rebasing,
  commit messages, pull requests, or version control workflows. Also trigger when
  helping write commit messages, resolving merge conflicts, or setting up Git hooks.
---

# Git Workflow & Conventions

## Commit Messages

Use conventional commits format:
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

### Types
- `feat` — New feature
- `fix` — Bug fix
- `refactor` — Code change that neither fixes a bug nor adds a feature
- `docs` — Documentation only
- `style` — Formatting, missing semicolons, etc (not CSS)
- `test` — Adding or correcting tests
- `chore` — Build process, CI, dependencies
- `perf` — Performance improvement
- `ci` — CI/CD changes
- `build` — Build system changes
- `revert` — Revert a previous commit

### Examples
```
feat(bids): add AI confidence score display to bid detail page
fix(procore): resolve OAuth token refresh race condition
refactor(hooks): consolidate useSubcontractor query patterns
docs(api): add Edge Function authentication examples
chore(deps): upgrade @tanstack/react-query to v5
test(auth): add RLS policy integration tests for bid table
perf(db): add trigram index for subcontractor fuzzy search
```

## Branching Strategy

```
main (production)
  └── develop (integration)
       ├── feature/add-bid-comparison
       ├── feature/procore-estimate-push
       ├── fix/parse-queue-stuck-items
       ├── refactor/consolidate-token-storage
       └── hotfix/critical-rls-bypass
```

### Branch Naming
- `feature/short-description` — New features
- `fix/issue-description` — Bug fixes
- `refactor/what-changed` — Refactors
- `hotfix/critical-issue` — Production emergency fixes
- `chore/maintenance-task` — Maintenance

## Common Workflows

### Start a feature
```bash
git checkout develop
git pull origin develop
git checkout -b feature/my-feature
# ... work ...
git add -A
git commit -m "feat(scope): description"
git push -u origin feature/my-feature
```

### Sync with develop
```bash
git checkout feature/my-feature
git fetch origin
git rebase origin/develop
# resolve conflicts if any
git push --force-with-lease
```

### Squash messy commits before PR
```bash
git rebase -i HEAD~3  # squash last 3 commits
# Change 'pick' to 'squash' for commits to combine
# Write clean combined commit message
git push --force-with-lease
```

### Undo last commit (keep changes)
```bash
git reset --soft HEAD~1
```

### Stash work in progress
```bash
git stash push -m "WIP: description"
git stash list
git stash pop
```

## PR Checklist
- [ ] Branch is up to date with target branch
- [ ] Commit messages follow conventional format
- [ ] No console.logs or debugging code left
- [ ] Database migrations are reversible
- [ ] RLS policies updated if new tables added
- [ ] TypeScript types updated
- [ ] Tests pass locally
- [ ] No secrets or API keys in code
