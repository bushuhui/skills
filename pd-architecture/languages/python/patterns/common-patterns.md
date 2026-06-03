# Python Architecture Patterns

## Repository Pattern

```python
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Optional

T = TypeVar('T')

class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def get(self, id: int) -> Optional[T]: ...
    @abstractmethod
    async def list(self, skip: int = 0, limit: int = 100) -> list[T]: ...
    @abstractmethod
    async def create(self, obj: T) -> T: ...
    @abstractmethod
    async def update(self, id: int, obj: T) -> Optional[T]: ...
    @abstractmethod
    async def delete(self, id: int) -> bool: ...
```

## Service Layer Pattern

```python
class UserService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def create_user(self, user_data: UserCreate) -> User:
        if await self._email_exists(user_data.email):
            raise ValueError("Email already registered")
        user = User(**user_data.model_dump())
        return await self.user_repo.create(user)
```

## Event Bus

```python
@dataclass
class Event:
    event_type: str
    data: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)

class EventBus:
    def __init__(self):
        self._subscribers: dict[str, list[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable):
        self._subscribers.setdefault(event_type, []).append(handler)

    async def publish(self, event: Event):
        await asyncio.gather(*[h(event) for h in self._subscribers.get(event.event_type, [])])
```

## Circuit Breaker

```python
class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 30):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.state = "closed"

    async def call(self, func, *args, **kwargs):
        if self.state == "open":
            if self._should_attempt_reset():
                self.state = "half_open"
            else:
                raise Exception("Circuit breaker is OPEN")
        try:
            result = await asyncio.wait_for(func(*args, **kwargs), timeout=10)
            self.failure_count = 0
            self.state = "closed"
            return result
        except Exception:
            self.failure_count += 1
            if self.failure_count >= self.failure_threshold:
                self.state = "open"
            raise

    def _should_attempt_reset(self) -> bool:
        return True  # Simplified — add time check in production
```

## Retry with Exponential Backoff

```python
def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 60.0):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            retries = 0
            while retries < max_retries:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        raise
                    delay = min(base_delay * (2 ** (retries - 1)), max_delay)
                    await asyncio.sleep(delay)
        return wrapper
    return decorator
```

## CQRS Implementation

```python
# Commands
class Command(Protocol): ...

class CommandHandler(ABC, Generic[TCommand]):
    @abstractmethod
    async def handle(self, command: TCommand) -> Any: ...

# Queries
class Query(Protocol): ...

class QueryHandler(ABC, Generic[TQuery]):
    @abstractmethod
    async def handle(self, query: TQuery) -> Any: ...
```

## Settings Management

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    secret_key: str
    log_level: str = "INFO"

    class Config:
        env_file = ".env"
        case_sensitive = False

from functools import lru_cache
@lru_cache()
def get_settings() -> Settings:
    return Settings()
```

## Structured Logging

```python
import structlog
structlog.configure(
    processors=[
        structlog.stdlib.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)
logger = structlog.get_logger()
logger.info("user_created", user_id=123, email="user@example.com")
```
