# Express.js Architecture Patterns

## Router Organization

### Bad — Single monolithic router

```typescript
// routes.ts — 500+ lines, all routes in one file
app.get("/users", ...);
app.post("/users", ...);
app.get("/users/:id", ...);
app.put("/users/:id", ...);
app.delete("/users/:id", ...);
app.get("/orders", ...);
// ... hundreds more
```

### Good — Modular routers with middleware chains

```typescript
// src/routes/index.ts
import { Router } from "express";
import userRoutes from "./user.routes";
import orderRoutes from "./order.routes";

const router = Router();
router.use("/users", userRoutes);
router.use("/orders", orderRoutes);
export default router;

// src/routes/user.routes.ts
import { Router } from "express";
import { authenticate, authorize } from "../middleware/auth";
import { validate } from "../middleware/validation";
import { CreateUserSchema } from "../schemas/user";
import { userController } from "../controllers";

const router = Router();
router.post("/", validate(CreateUserSchema), userController.create);
router.get("/", authenticate, userController.list);
router.get("/:id", authenticate, userController.getById);
router.put("/:id", authenticate, authorize("admin"), userController.update);
router.delete("/:id", authenticate, authorize("admin"), userController.remove);
export default router;
```

## Dependency Injection in Express

```typescript
// src/container.ts — Composition root
import { config } from "./config";
import { db } from "./db";
import { UserRepository } from "./repositories";
import { UserService } from "./services";
import { UserController } from "./controllers";

const userRepository = new UserRepository(db);
const userService = new UserService(userRepository);
export const userController = new UserController(userService);
```

Controllers are thin — they delegate to services:

```typescript
// src/controllers/user.controller.ts
export class UserController {
  constructor(private userService: UserService) {}

  async create(req: Request, res: Response, next: NextFunction) {
    try {
      const user = await this.userService.create(req.body);
      res.status(201).json(userToResponse(user));
    } catch (err) {
      next(err);
    }
  }
}
```

## Error Handling Middleware

```typescript
// src/middleware/error.ts
import { Request, Response, NextFunction } from "express";

export class AppError extends Error {
  constructor(
    public statusCode: number,
    public code: string,
    message: string,
  ) {
    super(message);
  }
}

export class NotFoundError extends AppError {
  constructor(resource: string) {
    super(404, "NOT_FOUND", `${resource} not found`);
  }
}

export class ValidationError extends AppError {
  constructor(public errors: Record<string, string[]>) {
    super(400, "VALIDATION_ERROR", "Validation failed");
  }
}

// Catch-all error handler (MUST be last middleware)
export function errorHandler(
  err: unknown,
  _req: Request,
  res: Response,
  _next: NextFunction,
) {
  if (err instanceof AppError) {
    return res.status(err.statusCode).json({
      error: { code: err.code, message: err.message },
    });
  }

  // Unknown error — log and return 500
  console.error(err);
  return res.status(500).json({
    error: { code: "INTERNAL_ERROR", message: "Internal server error" },
  });
}

// Async handler wrapper — catches rejected promises
export function asyncHandler(
  fn: (req: Request, res: Response, next: NextFunction) => Promise<void>,
) {
  return (req: Request, res: Response, next: NextFunction) =>
    fn(req, res, next).catch(next);
}
```

## Authentication / Authorization Middleware

```typescript
// src/middleware/auth.ts
import { Request, Response, NextFunction } from "express";
import jwt from "jsonwebtoken";

interface AuthRequest extends Request {
  user?: { id: string; role: string };
}

export function authenticate(req: AuthRequest, res: Response, next: NextFunction) {
  const token = req.headers.authorization?.replace("Bearer ", "");
  if (!token) return res.status(401).json({ error: { code: "UNAUTHORIZED" } });

  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET!) as { id: string; role: string };
    next();
  } catch {
    res.status(401).json({ error: { code: "INVALID_TOKEN" } });
  }
}

export function authorize(...roles: string[]) {
  return (req: AuthRequest, _res: Response, next: NextFunction) => {
    if (!req.user || !roles.includes(req.user.role)) {
      return res.status(403).json({ error: { code: "FORBIDDEN" } });
    }
    next();
  };
}
```

## Project Structure for Scalable Express Apps

```
src/
├── index.ts                 # App entry point, composition root
├── config/                  # Environment config, zod-validated
│   └── index.ts
├── routes/                  # Router definitions
│   ├── index.ts
│   ├── user.routes.ts
│   └── order.routes.ts
├── controllers/             # Request/response handling (thin)
│   ├── user.controller.ts
│   └── order.controller.ts
├── services/                # Business logic
│   ├── user.service.ts
│   └── order.service.ts
├── repositories/            # Data access
│   ├── user.repository.ts
│   └── order.repository.ts
├── middleware/              # Express middleware
│   ├── auth.ts
│   ├── error.ts
│   └── validation.ts
├── schemas/                 # Zod validation schemas
│   ├── user.ts
│   └── order.ts
├── domain/                  # Entities, value objects, domain errors
│   ├── user.ts
│   └── order.ts
└── types/                   # TypeScript type definitions
    └── index.ts
```
