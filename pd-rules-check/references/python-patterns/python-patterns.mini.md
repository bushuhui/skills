# OBEY Python Patterns

## When to use

Use when writing, reviewing, or refactoring Python code. Enforces readability, type safety, proper resource management, and idiomatic patterns.

## Primary bias to correct

Python code that works is not necessarily Pythonic -- readability and explicitness matter more than cleverness.

## Decision rules

- Readability first. Code should be obvious. Prefer clear names over clever one-liners.
- Explicit over implicit. No magic side effects, no hidden state. Configuration should be visible.
- EAFP: prefer exception handling over pre-checking conditions. Catch specific exceptions, never bare `except`.
- Type hints on all public functions. Use built-in types (`list`, `dict`) on Python 3.9+. `Optional`/`None` for nullable.
- Separate request/update/response models. Never expose ORM objects or password hashes in API responses.
- Use context managers (`with`) for all resource management. Custom `@contextmanager` for complex lifecycles.
- List comprehensions for simple transformations; generator expressions for large data; expand complex comprehensions into loops.
- Custom exception hierarchies with chaining (`raise ... from e`). Base app exception, domain-specific subclasses.
- Dataclasses for data containers with validation in `__post_init__`. `__slots__` for memory-critical classes.
- Decorators must use `@functools.wraps`. Parameterized decorators return a decorator factory.
- Async/await for concurrent I/O. `ThreadPoolExecutor` for I/O-bound, `ProcessPoolExecutor` for CPU-bound. Never block in async handlers.
- `src/` layout for packages. Import order: stdlib, third-party, local. Use `isort`.
- Avoid mutable default arguments, `type()` comparison, `== None`, `from x import *`, bare `except`.
- String concatenation in loops -- use `"".join()` or `StringIO` instead.

## Trigger rules

- When you see `items=[]` as a default, replace with `items=None` + `if items is None: items = []`.
- When `except:` catches everything, narrow to specific exceptions.
- When a function returns different types on success/failure, raise a custom exception instead.
- When a file/resource is opened without `with`, wrap in a context manager.
- When an ORM object is passed to JSON serialization, create a Pydantic response model.
- When `requests` is called in an async handler, use `httpx.AsyncClient` instead.
- When a loop builds a large string via `+=`, replace with `"".join()`.
- When type hints are missing on a public function, add them.
- When a comprehension has 3+ nested conditions, expand to a generator function.

## Final checklist

- All public functions type-annotated?
- No mutable default arguments?
- Context managers for all resource handling?
- Specific exception types caught, not bare `except`?
- Request/response models separated?
- No ORM objects leaking into responses?
- Async handlers use async I/O only?
- `@functools.wraps` on all decorators?
- Import order: stdlib, third-party, local?
- `isinstance` over `type()`, `is None` over `== None`?
- Tests use dependency overrides, not internal helper patches?
