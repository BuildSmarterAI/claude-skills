---
name: python-patterns
description: Pythonic idioms, PEP 8 standards, type hints, and best practices for building robust, efficient, and maintainable Python. Covers EAFP vs LBYL, container and concurrency decision matrices, advanced typing (ParamSpec, Self, overload, Protocol), comprehensions and generators, dataclasses, context managers, decorators, __slots__, packaging and the ruff / mypy / pytest toolchain.
origin: ECC
---

# Python Development Patterns

Deep reference for idiomatic Python. Extends `rules/python/` — see those for PEP 8, formatting tools, basic dataclasses, Protocol, pytest, secrets, and hook configuration. This file covers the harder decisions.

> Merged in D3.5 from two independently curated copies: the canonical decision-oriented spine
> plus the breadth sections (comprehensions, dataclasses, packaging, tooling, idiom reference)
> that existed only in the runtime copy. Neither side was discarded.

> Merged in D3.5 from two independently curated copies: the canonical decision-oriented spine
> plus the breadth sections (comprehensions, dataclasses, packaging, tooling, idiom reference)
> that existed only in the runtime copy. Neither side was discarded.

> Merged in D3.5 from two independently curated copies: the canonical decision-oriented spine
> plus the breadth sections (comprehensions, dataclasses, packaging, tooling, idiom reference)
> that existed only in the runtime copy. Neither side was discarded.

## When to Activate

Writing, reviewing, refactoring Python; designing packages/modules; resolving "which tool for the job" questions.

## Core Principles

### 1. Readability Counts

Python prioritizes readability. Code should be obvious and easy to understand.

```python
# Good: Clear and readable
def get_active_users(users: list[User]) -> list[User]:
    """Return only active users from the provided list."""
    return [user for user in users if user.is_active]


# Bad: Clever but confusing
def get_active_users(u):
    return [x for x in u if x.a]
```

### 2. Explicit is Better Than Implicit

Avoid magic; be clear about what your code does.

```python
# Good: Explicit configuration
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Bad: Hidden side effects
import some_module
some_module.setup()  # What does this do?
```

### 3. EAFP - Easier to Ask Forgiveness Than Permission

Python prefers exception handling over checking conditions.

```python
# Good: EAFP style
def get_value(dictionary: dict, key: str) -> Any:
    try:
        return dictionary[key]
    except KeyError:
        return default_value

# Bad: LBYL (Look Before You Leap) style
def get_value(dictionary: dict, key: str) -> Any:
    if key in dictionary:
        return dictionary[key]
    else:
        return default_value
```

## EAFP vs LBYL

Python prefers EAFP (Easier to Ask Forgiveness than Permission). Use LBYL only when the check is cheap and the failure cost is high (e.g., destructive operations).

```python
# EAFP — atomic, no race condition
try:
    return dictionary[key]
except KeyError:
    return default

# LBYL — race-prone, two lookups
if key in dictionary:
    return dictionary[key]
```

Exception: file existence checks before destructive ops, network preflight, permission gates.

## Decision Matrices

### Data container: which one?

| Use case | Choice |
|---|---|
| Internal DTO, mutable, methods | `@dataclass` |
| Immutable value object, hashable, tuple-like | `NamedTuple` or `@dataclass(frozen=True, slots=True)` |
| External I/O (HTTP, JSON), validation needed | `pydantic.BaseModel` |
| Static type-only shape (no runtime cost) | `TypedDict` |
| Hot path, millions of instances | `@dataclass(slots=True)` or `NamedTuple` |

`NamedTuple` is hashable, ordered, indexable. `frozen=True` dataclass is hashable but not indexable. `TypedDict` is a dict at runtime — zero overhead, no methods.

### Concurrency: which one?

| Workload | Choice | Reason |
|---|---|---|
| I/O-bound, < ~100 concurrent ops, sync libs | `ThreadPoolExecutor` | GIL released during I/O; simple |
| I/O-bound, thousands concurrent, async libs available | `asyncio` | One thread, cheap tasks |
| CPU-bound, parallelizable | `ProcessPoolExecutor` | Bypasses GIL |
| CPU-bound, not parallelizable | Optimize first; consider Cython/numpy/PyPy |
| Mixed CPU+I/O | `asyncio` + `loop.run_in_executor` for CPU chunks |

Pitfalls: never mix `asyncio` with blocking calls (use `asyncio.to_thread`); cross-process IPC must use `multiprocessing.Queue` or `Pipe` (don't try to share live object references); `multiprocessing` on Windows requires `if __name__ == "__main__":` guard.

## Advanced Type Hints

```python
from typing import TypeVar, Generic, Protocol, ParamSpec, Self, overload

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)
P = ParamSpec("P")

# Generic container
class Stack(Generic[T]):
    def push(self, item: T) -> None: ...
    def pop(self) -> T: ...

# Bounded TypeVar
Number = TypeVar("Number", int, float)
def double(x: Number) -> Number: return x * 2

# Protocol — structural typing, no inheritance needed
class SupportsClose(Protocol):
    def close(self) -> None: ...

# ParamSpec — preserve signature through decorators
def log_call(fn: Callable[P, T]) -> Callable[P, T]: ...

# Self — return type of fluent builders (3.11+)
class Builder:
    def with_name(self, n: str) -> Self: ...

# Overload — disambiguate return types
@overload
def parse(x: str) -> dict: ...
@overload
def parse(x: bytes) -> list: ...
def parse(x): ...
```

Use `from __future__ import annotations` to defer evaluation (allows forward refs without quotes; required for some recursive types pre-3.12).

## Comprehensions and Generators

### List Comprehensions

```python
# Good: List comprehension for simple transformations
names = [user.name for user in users if user.is_active]

# Bad: Manual loop
names = []
for user in users:
    if user.is_active:
        names.append(user.name)

# Complex comprehensions should be expanded
# Bad: Too complex
result = [x * 2 for x in items if x > 0 if x % 2 == 0]

# Good: Use a generator function
def filter_and_transform(items: Iterable[int]) -> list[int]:
    result = []
    for x in items:
        if x > 0 and x % 2 == 0:
            result.append(x * 2)
    return result
```

### Generator Expressions

```python
# Good: Generator for lazy evaluation
total = sum(x * x for x in range(1_000_000))

# Bad: Creates large intermediate list
total = sum([x * x for x in range(1_000_000)])
```

### Generator Functions

```python
def read_large_file(path: str) -> Iterator[str]:
    """Read a large file line by line."""
    with open(path) as f:
        for line in f:
            yield line.strip()

# Usage
for line in read_large_file("huge.txt"):
    process(line)
```

## Data Classes and Named Tuples

### Data Classes

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class User:
    """User entity with automatic __init__, __repr__, and __eq__."""
    id: str
    name: str
    email: str
    created_at: datetime = field(default_factory=datetime.now)
    is_active: bool = True

# Usage
user = User(
    id="123",
    name="Alice",
    email="alice@example.com"
)
```

### Data Classes with Validation

```python
@dataclass
class User:
    email: str
    age: int

    def __post_init__(self):
        # Validate email format
        if "@" not in self.email:
            raise ValueError(f"Invalid email: {self.email}")
        # Validate age range
        if self.age < 0 or self.age > 150:
            raise ValueError(f"Invalid age: {self.age}")
```

### Named Tuples

```python
from typing import NamedTuple

class Point(NamedTuple):
    """Immutable 2D point."""
    x: float
    y: float

    def distance(self, other: 'Point') -> float:
        return ((self.x - other.x) ** 2 + (self.y - other.y) ** 2) ** 0.5

# Usage
p1 = Point(0, 0)
p2 = Point(3, 4)
print(p1.distance(p2))  # 5.0
```

## Error Handling

### Custom hierarchy

```python
class AppError(Exception): pass
class ValidationError(AppError): pass
class NotFoundError(AppError): pass
class ConflictError(AppError): pass
```

Callers catch `AppError` for "any app problem", or specific subclasses. Never inherit from `BaseException` — that's for `SystemExit`/`KeyboardInterrupt`.

### Chaining: `raise ... from`

```python
try:
    parsed = json.loads(data)
except json.JSONDecodeError as e:
    raise ConfigError(f"Bad config at {path}") from e   # preserves __cause__
```

Use `from None` to suppress the original (rare — only when the inner exception is noise).

## Context Managers

### `@contextmanager` decorator (function form)

```python
from contextlib import contextmanager

@contextmanager
def timer(name: str):
    start = time.perf_counter()
    try:
        yield
    finally:
        print(f"{name}: {time.perf_counter() - start:.4f}s")
```

`try/finally` is mandatory if cleanup must run on exception.

### Class form — controlling exception propagation

```python
class Transaction:
    def __enter__(self): self.conn.begin(); return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None: self.conn.commit()
        else: self.conn.rollback()
        return False   # False = propagate; True = swallow
```

Returning `True` from `__exit__` suppresses the exception — use sparingly and document loudly.

### `contextlib.ExitStack`

```python
with ExitStack() as stack:
    files = [stack.enter_context(open(p)) for p in paths]   # dynamic N
```

## Decorators

### Function decorator — always use `functools.wraps`

```python
import functools
def timer(fn):
    @functools.wraps(fn)   # preserves __name__, __doc__, __wrapped__
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return fn(*args, **kwargs)
        finally:
            print(f"{fn.__name__}: {time.perf_counter() - start:.4f}s")
    return wrapper
```

Without `@functools.wraps`, introspection and `inspect.signature` break.

### Parameterized decorator (three-level)

```python
def retry(times: int, exceptions: tuple = (Exception,)):
    def decorator(fn):
        @functools.wraps(fn)
        def wrapper(*a, **kw):
            for attempt in range(times):
                try: return fn(*a, **kw)
                except exceptions:
                    if attempt == times - 1: raise
        return wrapper
    return decorator

@retry(times=3, exceptions=(IOError,))
def fetch(url): ...
```

### Class-based decorator (stateful)

```python
class CountCalls:
    def __init__(self, fn):
        functools.update_wrapper(self, fn)
        self.fn, self.count = fn, 0
    def __call__(self, *a, **kw):
        self.count += 1
        return self.fn(*a, **kw)
```

Use class form when the decorator holds state (counters, caches, registries).

## Concurrency: Worked Examples

```python
# I/O-bound, sync libs
with ThreadPoolExecutor(max_workers=10) as ex:
    results = list(ex.map(fetch_url, urls))

# CPU-bound
with ProcessPoolExecutor() as ex:
    results = list(ex.map(heavy_compute, datasets))

# I/O-bound, async
async def fetch_all(urls):
    async with aiohttp.ClientSession() as s:
        return await asyncio.gather(*(s.get(u) for u in urls))

# Async + blocking call
result = await asyncio.to_thread(legacy_blocking_fn, arg)
```

## Memory & Performance

### `__slots__` — fixed attribute set, ~40% smaller, faster access

```python
@dataclass(slots=True)   # 3.10+
class Point:
    x: float
    y: float
```

Caveats: no `__dict__`, can't add attributes at runtime, multiple inheritance is fiddly, doesn't compose with `weakref` unless you add `__weakref__` to slots.

### String building — never concatenate in a loop

```python
# O(n²)
s = ""
for item in items: s += str(item)

# O(n)
s = "".join(str(item) for item in items)
```

For complex assembly, use `io.StringIO`.

## Package Organization

### Standard Project Layout

```
myproject/
├── src/
│   └── mypackage/
│       ├── __init__.py
│       ├── main.py
│       ├── api/
│       │   ├── __init__.py
│       │   └── routes.py
│       ├── models/
│       │   ├── __init__.py
│       │   └── user.py
│       └── utils/
│           ├── __init__.py
│           └── helpers.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api.py
│   └── test_models.py
├── pyproject.toml
├── README.md
└── .gitignore
```

### Import Conventions

```python
# Good: Import order - stdlib, third-party, local
import os
import sys
from pathlib import Path

import requests
from fastapi import FastAPI

from mypackage.models import User
from mypackage.utils import format_name

# Good: Use isort for automatic import sorting
# pip install isort
```

### __init__.py for Package Exports

```python
# mypackage/__init__.py
"""mypackage - A sample Python package."""

__version__ = "1.0.0"

# Export main classes/functions at package level
from mypackage.models import User, Post
from mypackage.utils import format_name

__all__ = ["User", "Post", "format_name"]
```

## Package Exports

```python
# mypackage/__init__.py
from mypackage.models import User, Post
from mypackage.utils import format_name
__all__ = ["User", "Post", "format_name"]
__version__ = "1.0.0"
```

`__all__` controls `from pkg import *` AND signals public API to tools.

## pyproject.toml

```toml
[project]
name = "mypackage"
version = "1.0.0"
requires-python = ">=3.11"
dependencies = ["requests>=2.31", "pydantic>=2.0"]

[project.optional-dependencies]
dev = ["pytest>=8", "pytest-cov", "black", "ruff", "mypy"]

[tool.black]
line-length = 88
target-version = ["py311"]

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W", "UP", "B", "SIM"]

[tool.mypy]
python_version = "3.11"
strict = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=src --cov-report=term-missing --strict-markers"
markers = ["unit", "integration", "slow"]
```

## Python Tooling Integration

### Essential Commands

```bash
# Code formatting
black .
isort .

# Linting
ruff check .
pylint mypackage/

# Type checking
mypy .

# Testing
pytest --cov=mypackage --cov-report=html

# Security scanning
bandit -r .

# Dependency management
pip-audit
safety check
```

### pyproject.toml Configuration

```toml
[project]
name = "mypackage"
version = "1.0.0"
requires-python = ">=3.9"
dependencies = [
    "requests>=2.31.0",
    "pydantic>=2.0.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "black>=23.0.0",
    "ruff>=0.1.0",
    "mypy>=1.5.0",
]

[tool.black]
line-length = 88
target-version = ['py39']

[tool.ruff]
line-length = 88
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "--cov=mypackage --cov-report=term-missing"
```

## Quick Reference: Python Idioms

| Idiom | Description |
|-------|-------------|
| EAFP | Easier to Ask Forgiveness than Permission |
| Context managers | Use `with` for resource management |
| List comprehensions | For simple transformations |
| Generators | For lazy evaluation and large datasets |
| Type hints | Annotate function signatures |
| Dataclasses | For data containers with auto-generated methods |
| `__slots__` | For memory optimization |
| f-strings | For string formatting (Python 3.6+) |
| `pathlib.Path` | For path operations (Python 3.4+) |
| `enumerate` | For index-element pairs in loops |

## Anti-Patterns Worth Memorizing

```python
# Mutable default — shared across calls!
def bad(items=[]): items.append(1); return items

def good(items=None):
    if items is None: items = []
    items.append(1); return items

# Late-binding closure — all lambdas see final i
funcs = [lambda: i for i in range(3)]            # all return 2
funcs = [lambda i=i: i for i in range(3)]        # capture via default arg

# Modifying list during iteration
for x in lst:
    if cond(x): lst.remove(x)                    # skips items
lst[:] = [x for x in lst if not cond(x)]         # correct

# Class-level mutable
class C:
    items = []          # shared across all instances!
class C:
    def __init__(self): self.items = []          # per-instance
```

## Anti-Patterns to Avoid

```python
# Bad: Mutable default arguments
def append_to(item, items=[]):
    items.append(item)
    return items

# Good: Use None and create new list
def append_to(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items

# Bad: Checking type with type()
if type(obj) == list:
    process(obj)

# Good: Use isinstance
if isinstance(obj, list):
    process(obj)

# Bad: Comparing to None with ==
if value == None:
    process()

# Good: Use is
if value is None:
    process()

# Bad: from module import *
from os.path import *

# Good: Explicit imports
from os.path import join, exists

# Bad: Bare except
try:
    risky_operation()
except:
    pass

# Good: Specific exception
try:
    risky_operation()
except SpecificError as e:
    logger.error(f"Operation failed: {e}")
```

__Remember__: Python code should be readable, explicit, and follow the principle of least surprise. When in doubt, prioritize clarity over cleverness.

## Reference

- PEP 8, formatting, basic types: `rules/python/coding-style.md`
- Protocol, DTOs, basic generators: `rules/python/patterns.md`
- pytest, fixtures, markers: skill `python-testing`
- Secrets, bandit: `rules/python/security.md`
- Format/lint hooks: `rules/python/hooks.md`
