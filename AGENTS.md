<!-- This file was generated with the assistance of an AI coding tool. -->

# AGENTS.md

Guidelines for AI coding agents contributing to IfcOpenShell. This file is
intended to be read by all AI agents regardless of platform (Claude Code,
Copilot, Cursor, etc.) in addition to any tool-specific configuration files.

Human contributors using AI tools should also read this document carefully,
as they are responsible for ensuring their contributions comply with these
guidelines.

## Project Overview

IfcOpenShell is an open source library for working with Industry Foundation
Classes (IFC). It provides C++ and Python APIs, geometry processing, and an
ecosystem of tools including IfcConvert and the Bonsai Blender add-on.

## Licensing

All contributions must be compatible with the project's licensing:

- **Library code** (everything except Bonsai): **LGPL-3.0-or-later**
- **Bonsai** (`src/bonsai/`): **GPL-3.0-or-later**

There is no Contributor License Agreement (CLA). By submitting a pull request,
you agree that your contribution is licensed under the applicable license above.

## Indicating AI-Generated Code

Contributors must clearly indicate when code has been generated or
substantially written by an AI tool.

### Commits

Commits that modify existing code must include a note in the **body** of the
commit message (not the subject line) indicating that the change was
AI-generated. For example:

```
Fix off-by-one error in element iteration

The loop termination condition was incorrect when processing
IfcRelAggregates relationships.

Generated with the assistance of an AI coding tool.
```

### New Files

New files that are AI-generated must include a comment near the top of the
file indicating this. Use the appropriate comment syntax for the language:

```python
# This file was generated with the assistance of an AI coding tool.
```

```cpp
// This file was generated with the assistance of an AI coding tool.
```

### Pull Requests

Pull requests containing AI-generated code must indicate in the PR description
which parts of the contribution are AI-generated. If the entire PR is
AI-generated, state that clearly. If only specific commits or files are
AI-generated, identify them.

## Pull Request Guidelines

### Scope and Size

- Each pull request should address a **single issue or feature**.
- Do not mix unrelated changes (e.g., bug fixes with refactoring or style
  changes) in the same PR.
- Large pull requests should be broken down into **multiple small, standalone
  commits** that are each easy to review independently. Rewrite commit history
  for this purpose if necessary.
- PRs that are minimal, focused solutions to a specific problem are much more
  likely to be accepted.

### What to Avoid

- **Over-engineering**: Do not add features, abstractions, or configurability
  beyond what is needed to solve the immediate problem.
- **Scope creep**: Do not make changes to files or code that are not directly
  related to the task at hand.
- **Unnecessary additions**: Do not add docstrings, comments, type annotations,
  or error handling to code you did not otherwise need to change.
- **Cosmetic changes**: Do not reformat, rename, or reorganize code that is
  unrelated to your change.

## Commit Messages

- The **subject line** must be **50 characters or less**.
- Use the **imperative mood** (e.g., "Fix crash in geometry kernel", not
  "Fixed crash" or "Fixes crash").
- A commit message can be a single line if the purpose is obvious from the
  subject alone.
- Otherwise, add a blank line after the subject followed by a short explanation
  of a few lines in the body.

## Code Style

### Python

- **Line length**: 120 characters
- **Formatter**: black
- **Linter**: ruff
- Configuration is in `pyproject.toml`

### C++

- **Standard**: C++17 minimum
- **Formatter**: clang-format (configuration in `.clang-format`)
- **Linter**: clang-tidy (configuration in `.clang-tidy`)

Run linters and formatters **before submitting** your pull request. Do not rely
on CI to catch formatting issues.

## Testing

- Pull requests with test coverage are **much more likely to be merged**.
- If tests are appropriate and feasible for your change, they should be
  included.
- Tests are not required for every change (e.g., documentation-only changes),
  but the expectation is that testable code changes come with tests.
- Python tests use **pytest** and are located in `test/` or `tests/` directories
  within each package under `src/`.
- Run the existing test suite for the package you modified before submitting.

## Architecture Quick Reference

### Directory Structure

- `src/ifcparse/` — C++ IFC file parsing
- `src/ifcgeom/` — C++ geometry processing (OpenCASCADE and CGAL kernels)
- `src/serializers/` — Output format serializers (glTF, Collada, SVG, etc.)
- `src/ifcwrap/` — SWIG Python bindings
- `src/ifcconvert/` — CLI conversion tool
- `src/ifcopenshell-python/` — Python API (`ifcopenshell` package)
- `src/bonsai/` — Blender add-on (GPL-3.0-or-later)
- `src/ifctester/` — IDS model auditing
- `src/ifcpatch/` — IFC file manipulation scripts
- `src/ifcdiff/` — IFC model comparison
- `src/ifcclash/` — Clash detection
- `src/ifccsv/` — Schedule import/export

### IFC Schema Versions

The library supports IFC2x3 TC1, IFC4 Add2 TC1, IFC4x1, IFC4x2, and
IFC4x3 Add2. Schema-specific code is compiled conditionally. Be aware of
which schema versions your change affects.
