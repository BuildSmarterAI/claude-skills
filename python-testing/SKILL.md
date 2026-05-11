---
name: python-testing
description: Python testing strategies using pytest, TDD methodology, fixtures, mocking, parametrization, and coverage requirements.
origin: ECC
---

# Python Testing Patterns

Senior pytest reference card. Recipes for the things that actually trip people up.

> TDD philosophy lives in `superpowers:test-driven-development`. Coverage minimums (80%), AAA structure, and descriptive naming live in `~/.claude/rules/common/testing.md`. Framework choice (pytest) and `pytest.mark` categorization live in `~/.claude/rules/python/testing.md`. **This skill is the pytest cookbook.**

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
