# Python Patterns — Nano

Readability first. EAFP: catch specific exceptions, never bare `except`. Type hints on all public functions. Context managers (`with`) for resources. List comprehensions for simple, generators for large data. Dataclasses with `__post_init__` validation. `@functools.wraps` on decorators. Async I/O only in async handlers. `src/` layout. No mutable defaults, no `== None`, no `type()`, no `from x import *`. `"".join()` for loop string building. Separate request/response models.
