# FastAPI Architecture Patterns

## Basic Application

```python
app = FastAPI(title="My API", version="1.0.0")

class Item(BaseModel):
    name: str
    price: float

@app.post("/items", response_model=Item)
def create_item(item: Item):
    return item
```

## Routers for Organization

```python
# routers/users.py
router = APIRouter(prefix="/users", tags=["users"])
@router.get("/")
def list_users(): ...

# main.py
app.include_router(users.router)
```

## Dependency Injection

```python
def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/users")
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
```

**Nested dependencies:**
```python
def get_user_repo(db: Session = Depends(get_db)):
    return UserRepository(db)

def get_user_service(repo: UserRepository = Depends(get_user_repo)):
    return UserService(repo)

@app.get("/users/{id}")
def get_user(id: int, service: UserService = Depends(get_user_service)):
    return service.get_user(id)
```

## Error Handling

```python
@app.exception_handler(BusinessError)
async def business_error_handler(request: Request, exc: BusinessError):
    return JSONResponse(status_code=400, content={"error": exc.message})
```

## Recommended Project Structure

```
my-api/
├── main.py                   # FastAPI app
├── routers/                  # Route handlers by resource
├── schemas/                  # Pydantic models (request/response)
├── services/                 # Business logic
├── repositories/             # Data access (abstract + implementation)
├── entities/                 # Domain models (dataclasses)
└── dependencies.py           # Shared dependency injection
```

## Best Practices

1. Always define explicit `response_model`
2. Validate inputs with Pydantic constraints
3. Use dependency injection for sessions, auth, cross-cutting concerns
4. Split routes by resource/domain with routers
5. Use HTTP exceptions and custom handlers for errors
6. Type hints are required — FastAPI uses them for validation and docs
