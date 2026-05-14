# C++ Coding Standards — Nano

RAII always. No raw `new`/`delete`/`malloc`. `const`/`constexpr` default. `enum class` not `enum`. `nullptr` not `0`/`NULL`. No C-style casts. Single-arg constructors `explicit`. Rule of Zero or Five. Virtual destructor: public virtual or protected non-virtual. Use `override`/`final`. No globals, no `using namespace` in headers. Headers self-contained with guards. `std::scoped_lock` for mutexes. Templates constrained with concepts. Measure before optimizing. Throw custom types by value, catch by reference.
