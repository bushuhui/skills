# OBEY C++ Coding Standards (C++ Core Guidelines)

## When to use

Use when writing, reviewing, or refactoring C++ (C++17/20/23) code. Enforces type safety, resource safety, immutability, and clarity across all language levels.

## Primary bias to correct

C++ gives you enough rope to hang yourself -- modern defaults and the type system should prevent errors at compile time, not runtime.

## Decision rules

- RAII everywhere. Bind resource lifetime to object lifetime. No naked `new`/`delete`, no `malloc`/`free`.
- Immutability by default. `const`/`constexpr` unless mutation is intended and necessary.
- Type safety through the type system. Use `enum class`, strong types, concepts. No C-style casts.
- Express intent. Names, types, and concepts must communicate purpose. No Hungarian notation, no magic numbers.
- Keep functions short and single-purpose. Cheap params by value, others by `const&`. Return structs for multiple outputs.
- Rule of Zero when possible; Rule of Five when you must manage resources. Use `std::make_unique`/`std::make_shared`.
- Virtual destructors: public `virtual` or protected non-virtual. Use `override`/`final`, never repeat `virtual`.
- No non-const global variables. No `using namespace` at global scope in headers.
- Headers must be self-contained with include guards. Use `.cpp`/`.h` extensions.
- Concurrency: lock-free only when absolutely necessary. RAII locks always. Never hold a lock while calling unknown code.
- Templates must be constrained with concepts. Prefer `constexpr` over template metaprogramming when possible.
- Performance: measure before optimizing. Contiguous data for cache-friendliness. Compile-time computation where possible.

## Trigger rules

- When you see `new` or `delete`, replace with smart pointer or RAII wrapper.
- When a constructor takes a single argument, make it `explicit`.
- When a plain `enum` leaks names into the surrounding scope, convert to `enum class`.
- When multiple `lock()` calls appear, use `std::scoped_lock` for deadlock-free acquisition.
- When an unconstrained template appears, add a concept.
- When `std::endl` is used for line breaks, replace with `'\n'`.
- When a raw pointer represents ownership, convert to `unique_ptr` or `shared_ptr`.
- When narrowing conversions or C-style casts appear, use `static_cast` or brace-init.
- When cleanup code spreads across multiple paths, wrap in an RAII class.

## Final checklist

- No raw `new`/`delete` -- smart pointers or RAII only?
- All objects initialized at declaration?
- Variables `const`/`constexpr` by default?
- `enum class` instead of plain `enum`?
- `nullptr` instead of `0`/`NULL`?
- No C-style casts or narrowing conversions?
- Single-argument constructors `explicit`?
- Rule of Zero or Rule of Five applied?
- Virtual destructors correct in base classes?
- Templates constrained with concepts?
- Headers self-contained with include guards?
- RAII locks (`scoped_lock`/`lock_guard`) only?
- Custom exception types, thrown by value, caught by reference?
- No magic numbers or ALL_CAPS for non-macros?
