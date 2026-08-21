---
name: python-testing
description: Python testing with pytest: fixture scopes and conftest layering, readable parametrize ids, markers, mocking (patch vs MagicMock vs autospec, including the patch-target binding trap), async tests, exceptions and side effects, tmp_path/monkeypatch, FastAPI/Flask clients, SQLAlchemy transaction-per-test, and coverage gates that actually fail CI.
origin: ECC
---

# Python Testing Patterns

Senior pytest reference card. Recipes for the things that actually trip people up.

> TDD philosophy lives in `superpowers:test-driven-development`. Coverage minimums (80%), AAA structure, and descriptive naming live in `~/.claude/rules/common/testing.md`. Framework choice (pytest) and `pytest.mark` categorization live in `~/.claude/rules/python/testing.md`. **This skill is the pytest cookbook.**

> Merged in D3.5 from two independently curated copies. The canonical copy contributed the
> specialised material - fixture scopes, the patch-vs-autospec binding trap, SAVEPOINT
> transaction-per-test, coverage gates - and the runtime copy contributed breadth (async,
> exceptions, side effects, markers, organisation). Neither side was discarded.

> Merged in D3.5 from two independently curated copies. The canonical copy contributed the
> specialised material - fixture scopes, the patch-vs-autospec binding trap, SAVEPOINT
> transaction-per-test, coverage gates - and the runtime copy contributed breadth (async,
> exceptions, side effects, markers, organisation). Neither side was discarded.

## When to Activate

- Writing new Python code (follow TDD: red, green, refactor)
- Designing test suites for Python projects
- Reviewing Python test coverage
- Setting up testing infrastructure

## Core Testing Philosophy

### Test-Driven Development (TDD)

Always follow the TDD cycle:

1. **RED**: Write a failing test for the desired behavior
2. **GREEN**: Write minimal code to make the test pass
3. **REFACTOR**: Improve code while keeping tests green

```python
# Step 1: Write failing test (RED)
def test_add_numbers():
    result = add(2, 3)
    assert result == 5

# Step 2: Write minimal implementation (GREEN)
def add(a, b):
    return a + b

# Step 3: Refactor if needed (REFACTOR)
```

### Coverage Requirements

- **Target**: 80%+ code coverage
- **Critical paths**: 100% coverage required
- Use `pytest --cov` to measure coverage

```bash
pytest --cov=mypackage --cov-report=term-missing --cov-report=html
```

## pytest Fundamentals

### Basic Test Structure

```python
import pytest

def test_addition():
    """Test basic addition."""
    assert 2 + 2 == 4

def test_string_uppercase():
    """Test string uppercasing."""
    text = "hello"
    assert text.upper() == "HELLO"

def test_list_append():
    """Test list append."""
    items = [1, 2, 3]
    items.append(4)
    assert 4 in items
    assert len(items) == 4
```

### Assertions

```python
# Equality
assert result == expected

# Inequality
assert result != unexpected

# Truthiness
assert result  # Truthy
assert not result  # Falsy
assert result is True  # Exactly True
assert result is False  # Exactly False
assert result is None  # Exactly None

# Membership
assert item in collection
assert item not in collection

# Comparisons
assert result > 0
assert 0 <= result <= 100

# Type checking
assert isinstance(result, str)

# Exception testing (preferred approach)
with pytest.raises(ValueError):
    raise ValueError("error message")

# Check exception message
with pytest.raises(ValueError, match="invalid input"):
    raise ValueError("invalid input provided")

# Check exception attributes
with pytest.raises(ValueError) as exc_info:
    raise ValueError("error message")
assert str(exc_info.value) == "error message"
```

## Fixture Scopes — Picking the Right One

Default scope is `function`. Bigger scope = faster suite, more shared state risk.

```python
@pytest.fixture                              # per test (default) - safest
@pytest.fixture(scope="class")               # per TestClass
@pytest.fixture(scope="module")              # per .py file
@pytest.fixture(scope="package")             # per package (rare)
@pytest.fixture(scope="session")             # once per `pytest` invocation
```

**When `function` is wrong**: spinning up a Docker container, compiling a model, or starting an event loop per test makes the suite glacial. Hoist to `session`.

**When `session` is wrong**: any fixture that yields mutable state (DB connection, in-memory dict). One test mutates it, the next sees the mutation. If you must use `session` scope for an expensive resource, layer a `function`-scoped fixture on top that gives each test an isolated view (e.g. a SAVEPOINT — see SQLAlchemy section).

**Async event-loop pitfall**: pytest-asyncio's default `event_loop` is function-scoped. A `session`-scoped async fixture that touches it will raise `RuntimeError: ... attached to a different loop`. Override:

```python
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
```

In `pytest-asyncio >= 0.23`, prefer setting `asyncio_mode = "auto"` and `loop_scope` on the marker instead.

## conftest.py Layering

Pytest walks **upward** from the test file collecting `conftest.py` files. Fixtures defined closer to the test override ones higher up by name.

```
tests/
├── conftest.py              # session-wide: db_engine, app_factory
├── unit/
│   ├── conftest.py          # unit-only: mocked_redis
│   └── test_models.py
└── integration/
    ├── conftest.py          # integration: real_redis, http_client
    └── test_api.py
```

**Rules of thumb**:

- Put a fixture in the **highest** `conftest.py` that all consumers share — duplicates across files are a smell.
- Override by re-defining the same fixture name in a lower `conftest.py`. Pytest auto-resolves; no inheritance syntax needed.
- A fixture in `tests/conftest.py` is visible to all of `tests/`. A fixture in `src/mypkg/conftest.py` is only visible if pytest's `rootdir` includes it. Keep test fixtures under `tests/`.
- Don't import fixtures from `conftest.py` directly — let pytest discover them via dependency injection.

## parametrize — Make Failures Readable

```python
@pytest.mark.parametrize("email,valid", [
    ("alice@example.com", True),
    ("no-at-sign", False),
    ("@no-local.com", False),
    ("", False),
], ids=["plain", "missing-at", "missing-local", "empty"])
def test_email_validation(email, valid):
    assert is_valid_email(email) is valid
```

Without `ids=`, pytest renders test IDs like `test_email_validation[no-at-sign-False]` for strings but `test_email_validation[case3]` for complex objects — unreadable in CI logs.

**Per-case marks** (skip one case without losing the rest):

```python
@pytest.mark.parametrize("backend", [
    "sqlite",
    pytest.param("postgres", marks=pytest.mark.integration),
    pytest.param("mysql", marks=pytest.mark.skip(reason="MySQL CI broken")),
    pytest.param("oracle", marks=pytest.mark.xfail(reason="not supported")),
])
def test_backend(backend): ...
```

**Indirect parametrization** routes the param through a fixture (use when each case needs setup logic):

```python
@pytest.fixture
def db(request):
    return Database(url=DB_URLS[request.param])

@pytest.mark.parametrize("db", ["sqlite", "postgres"], indirect=True)
def test_query(db):
    assert db.query("SELECT 1") == [(1,)]
```

## Markers and Test Selection

### Custom Markers

```python
# Mark slow tests
@pytest.mark.slow
def test_slow_operation():
    time.sleep(5)

# Mark integration tests
@pytest.mark.integration
def test_api_integration():
    response = requests.get("https://api.example.com")
    assert response.status_code == 200

# Mark unit tests
@pytest.mark.unit
def test_unit_logic():
    assert calculate(2, 3) == 5
```

### Run Specific Tests

```bash
# Run only fast tests
pytest -m "not slow"

# Run only integration tests
pytest -m integration

# Run integration or slow tests
pytest -m "integration or slow"

# Run tests marked as unit but not slow
pytest -m "unit and not slow"
```

### Configure Markers in pytest.ini

```ini
[pytest]
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    django: marks tests as requiring Django
```

## Mocking — patch vs MagicMock vs autospec

**Patch where the name is *used*, not where it's defined.** This is the #1 mocking bug.

```python
# myapp/service.py
from myapp.client import fetch_user      # imported into service's namespace

# WRONG — patches the original, but service.py already bound its own reference
@patch("myapp.client.fetch_user")
def test_service(_): ...

# RIGHT
@patch("myapp.service.fetch_user")
def test_service(_): ...
```

**Mock class cheat sheet**:

| Use | When |
|---|---|
| `Mock()` | Plain stub. Accepts any attribute/call. |
| `MagicMock()` | Default for `patch()`. Adds dunder support (`__len__`, `__iter__`, context-manager). |
| `AsyncMock()` | For `async def` functions. `.assert_awaited_once()` instead of `.assert_called_once()`. |
| `patch(..., autospec=True)` | Mock matches the real callable's signature. Catches `db.qury(...)` typos. **Use by default.** |
| `patch(..., spec=Foo)` | Like autospec but for class instances. Restricts attributes to those on `Foo`. |
| `mock_open(read_data="...")` | Mock `open()` including context-manager protocol. |

**Side effects**:

```python
mock.return_value = 42              # always returns 42
mock.side_effect = ValueError       # raises on call
mock.side_effect = [1, 2, 3]        # returns each in sequence, StopIteration after
mock.side_effect = lambda x: x * 2  # dynamic response
```

**Async mocking** (`AsyncMock` is auto-applied if patching an `async def`, but not for arbitrary callables returning coroutines):

```python
@patch("myapp.service.fetch_user", new_callable=AsyncMock)
async def test_service(mock_fetch):
    mock_fetch.return_value = {"id": 1}
    result = await service.get_user(1)
    mock_fetch.assert_awaited_once_with(1)
```

## Testing Async Code

### Async Tests with pytest-asyncio

```python
import pytest

@pytest.mark.asyncio
async def test_async_function():
    """Test async function."""
    result = await async_add(2, 3)
    assert result == 5

@pytest.mark.asyncio
async def test_async_with_fixture(async_client):
    """Test async with async fixture."""
    response = await async_client.get("/api/users")
    assert response.status_code == 200
```

### Async Fixture

```python
@pytest.fixture
async def async_client():
    """Async fixture providing async test client."""
    app = create_app()
    async with app.test_client() as client:
        yield client

@pytest.mark.asyncio
async def test_api_endpoint(async_client):
    """Test using async fixture."""
    response = await async_client.get("/api/data")
    assert response.status_code == 200
```

### Mocking Async Functions

```python
@pytest.mark.asyncio
@patch("mypackage.async_api_call")
async def test_async_mock(api_call_mock):
    """Test async function with mock."""
    api_call_mock.return_value = {"status": "ok"}

    result = await my_async_function()

    api_call_mock.assert_awaited_once()
    assert result["status"] == "ok"
```

## Testing Exceptions

### Testing Expected Exceptions

```python
def test_divide_by_zero():
    """Test that dividing by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError):
        divide(10, 0)

def test_custom_exception():
    """Test custom exception with message."""
    with pytest.raises(ValueError, match="invalid input"):
        validate_input("invalid")
```

### Testing Exception Attributes

```python
def test_exception_with_details():
    """Test exception with custom attributes."""
    with pytest.raises(CustomError) as exc_info:
        raise CustomError("error", code=400)

    assert exc_info.value.code == 400
    assert "error" in str(exc_info.value)
```

## Testing Side Effects

### Testing File Operations

```python
import tempfile
import os

def test_file_processing():
    """Test file processing with temp file."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("test content")
        temp_path = f.name

    try:
        result = process_file(temp_path)
        assert result == "processed: test content"
    finally:
        os.unlink(temp_path)
```

### Testing with pytest's tmp_path Fixture

```python
def test_with_tmp_path(tmp_path):
    """Test using pytest's built-in temp path fixture."""
    test_file = tmp_path / "test.txt"
    test_file.write_text("hello world")

    result = process_file(str(test_file))
    assert result == "hello world"
    # tmp_path automatically cleaned up
```

### Testing with tmpdir Fixture

```python
def test_with_tmpdir(tmpdir):
    """Test using pytest's tmpdir fixture."""
    test_file = tmpdir.join("test.txt")
    test_file.write("data")

    result = process_file(str(test_file))
    assert result == "data"
```

## tmp_path and monkeypatch

`tmp_path` is a `pathlib.Path` unique per test, auto-cleaned. Prefer it over `tempfile`.

```python
def test_write_config(tmp_path):
    cfg = tmp_path / "config.yaml"
    cfg.write_text("debug: true")
    assert load_config(cfg).debug is True
```

`tmp_path_factory` (session-scoped) for fixtures that build expensive on-disk state once.

`monkeypatch` reverts automatically at test teardown. Use for env vars, attributes, `sys.path`, `os.chdir`:

```python
def test_with_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "test-key")
    monkeypatch.setattr("myapp.client.TIMEOUT", 0.1)
    monkeypatch.delenv("AWS_PROFILE", raising=False)
    monkeypatch.chdir(tmp_path)
    monkeypatch.syspath_prepend("/fake/path")
    # all reverted at test end
```

Prefer `monkeypatch.setattr` over `patch` for simple attribute swaps — no decorator stacking, no `with` block.

## FastAPI / Flask Test Clients

**FastAPI** — use `TestClient` (sync, wraps starlette's) or `httpx.AsyncClient` for async. Override dependencies instead of patching:

```python
from fastapi.testclient import TestClient
from myapp.main import app
from myapp.deps import get_db

@pytest.fixture
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()

def test_create_user(client):
    r = client.post("/users", json={"name": "Alice"})
    assert r.status_code == 201
    assert r.json()["name"] == "Alice"
```

For async tests, `httpx.AsyncClient(transport=ASGITransport(app=app), base_url="http://test")` — `TestClient` won't run async fixtures correctly inside the same event loop.

**Flask** — push an app context for anything that touches `current_app`, `g`, or `url_for`:

```python
@pytest.fixture
def app():
    app = create_app({"TESTING": True})
    with app.app_context():
        yield app

@pytest.fixture
def client(app):
    return app.test_client()
```

## SQLAlchemy — Transaction Per Test (SAVEPOINT)

Naive "rollback at teardown" fails when application code calls `session.commit()`. The right pattern wraps every test in an outer transaction with a nested SAVEPOINT that auto-restarts on commit:

```python
@pytest.fixture(scope="session")
def engine():
    eng = create_engine("postgresql://localhost/test")
    Base.metadata.create_all(eng)
    yield eng
    eng.dispose()

@pytest.fixture
def db_session(engine):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    session.begin_nested()  # SAVEPOINT

    @event.listens_for(session, "after_transaction_end")
    def restart_savepoint(sess, trans):
        if trans.nested and not trans._parent.nested:
            sess.begin_nested()

    yield session

    session.close()
    transaction.rollback()  # rolls back ALL nested commits
    connection.close()
```

Tests can `session.commit()` freely; everything is undone at teardown. ~100x faster than truncating tables between tests.

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── __init__.py
├── unit/                       # Unit tests
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_utils.py
│   └── test_services.py
├── integration/                # Integration tests
│   ├── __init__.py
│   ├── test_api.py
│   └── test_database.py
└── e2e/                        # End-to-end tests
    ├── __init__.py
    └── test_user_flow.py
```

### Test Classes

```python
class TestUserService:
    """Group related tests in a class."""

    @pytest.fixture(autouse=True)
    def setup(self):
        """Setup runs before each test in this class."""
        self.service = UserService()

    def test_create_user(self):
        """Test user creation."""
        user = self.service.create_user("Alice")
        assert user.name == "Alice"

    def test_delete_user(self):
        """Test user deletion."""
        user = User(id=1, name="Bob")
        self.service.delete_user(user)
        assert not self.service.user_exists(1)
```

## Coverage — Gates That Actually Fail CI

Bare `--cov` reports but doesn't fail the build. Use `--cov-fail-under` to enforce the rules/common 80% minimum:

```bash
pytest --cov=src --cov-branch --cov-report=term-missing --cov-fail-under=80
```

- `--cov-branch` catches `if x:` taken only one way (line coverage marks it green).
- `--cov-report=xml` for Codecov / SonarQube; `=html` for local exploration.
- `--cov-config=.coveragerc` to exclude `__repr__`, `if TYPE_CHECKING:`, `raise NotImplementedError`, etc.

`.coveragerc`:

```ini
[run]
branch = True
source = src
omit = */migrations/*, */tests/*

[report]
exclude_lines =
    pragma: no cover
    raise NotImplementedError
    if TYPE_CHECKING:
    if __name__ == .__main__.:
```

## pytest Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --disable-warnings
    --cov=mypackage
    --cov-report=term-missing
    --cov-report=html
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
```

### pyproject.toml

```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--cov=mypackage",
    "--cov-report=term-missing",
    "--cov-report=html",
]
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
    "unit: marks tests as unit tests",
]
```

## Running Tests

```bash
# Run all tests
pytest

# Run specific file
pytest tests/test_utils.py

# Run specific test
pytest tests/test_utils.py::test_function

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=mypackage --cov-report=html

# Run only fast tests
pytest -m "not slow"

# Run until first failure
pytest -x

# Run and stop on N failures
pytest --maxfail=3

# Run last failed tests
pytest --lf

# Run tests with pattern
pytest -k "test_user"

# Run with debugger on failure
pytest --pdb
```

## Useful Flags Worth Memorizing

| Flag | What it does |
|---|---|
| `-x` | Stop after first failure |
| `--lf` | Re-run only last-failed tests |
| `--ff` | Run failed first, then the rest |
| `-k "user and not slow"` | Filter by name expression |
| `-m "integration"` | Filter by marker |
| `--pdb` | Drop into debugger on failure |
| `-s` | Don't capture stdout (show `print`) |
| `-rA` | Show short summary for ALL outcomes (pass/skip/xfail) |
| `--co` | Collect-only — list tests without running |
| `-p no:cacheprovider` | Disable `.pytest_cache` (CI) |
| `--durations=10` | Report 10 slowest tests |
| `-n auto` | Parallel via pytest-xdist (one proc per CPU) |

## Quick Reference

| Pattern | Usage |
|---------|-------|
| `pytest.raises()` | Test expected exceptions |
| `@pytest.fixture()` | Create reusable test fixtures |
| `@pytest.mark.parametrize()` | Run tests with multiple inputs |
| `@pytest.mark.slow` | Mark slow tests |
| `pytest -m "not slow"` | Skip slow tests |
| `@patch()` | Mock functions and classes |
| `tmp_path` fixture | Automatic temp directory |
| `pytest --cov` | Generate coverage report |
| `assert` | Simple and readable assertions |

**Remember**: Tests are code too. Keep them clean, readable, and maintainable. Good tests catch bugs; great tests prevent them.
