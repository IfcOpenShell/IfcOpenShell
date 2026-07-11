# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository conventions (read AGENTS.md)

**This project's contribution rules live in [AGENTS.md](AGENTS.md) — read it in full before
making changes.** It is binding on all AI agents, not just advisory. Key points to apply on
every task:

- **AI-generated code disclosure is mandatory:**
  - Commits that modify existing code must note AI assistance in the commit **body** (not the
    subject line), e.g. `Generated with the assistance of an AI coding tool.`
  - New AI-generated files must carry a top-of-file comment: `# This file was generated with
    the assistance of an AI coding tool.` (or the language's comment syntax).
  - Any PR description must state which parts (or all) of the contribution are AI-generated.
- **Commit messages:** subject line ≤50 chars, imperative mood ("Fix crash", not "Fixed crash").
  Add a body only when the subject alone doesn't explain the change.
- **PR scope:** one issue/feature per PR. Don't mix bug fixes with refactors or style changes.
  Split large changes into small, independently-reviewable commits. Don't touch unrelated files,
  and don't add docstrings/comments/type annotations/error handling beyond what the task needs.
- **Code style:** Python is formatted with `black` and linted with `ruff`, 120-char line length
  (config in `pyproject.toml`). C++ uses clang-format/clang-tidy (`.clang-format`/`.clang-tidy`),
  C++17 minimum. Run formatters/linters before considering work done — don't rely on CI.
- **Licensing:** everything under `src/bonsai/` is GPL-3.0-or-later; everything else is
  LGPL-3.0-or-later.

## Commands

Environments are managed with [pixi](https://pixi.sh) (`pixi.toml`) and [poe](https://github.com/nat-n/poethepoet)
tasks (`pyproject.toml`). CI (`.github/workflows/ci-lint.yaml`) is the source of truth for what
must pass.

### Lint / format (Python, whole repo)
```
ruff check                      # lint
black .                         # format in place
black --diff --check .          # format check only (what CI runs)
poe format                      # black then ruff, via poe
```

### Type checking (`ty`)
```
poe ty-venv     # one-time: create the two type-check venvs (bonsai + ifcopenshell-python)
poe ty          # runs ty-bonsai and ty-ios
```

### C++ build
Root-level C++ build is driven by CMake via pixi tasks (Windows-focused presets are defined in
`pixi.toml`; on Linux/macOS use `nix/build-all.py` or the presets under `cmake/`). See
`README.md` / `docs` for platform-specific install instructions before doing a full C++ build —
it's a heavy, multi-dependency build (OpenCASCADE, CGAL, SWIG, etc.) and isn't needed for most
Python-only or Bonsai-only changes.

### ifcopenshell-python tests
```
cd src/ifcopenshell-python/test
pytest .                          # full suite
pytest test_open.py               # single file
pytest test_open.py::test_name    # single test
```
Requires a built/installed `ifcopenshell` on `PYTHONPATH` (the pixi `tests` env's `test` task
builds it first — see `pixi.toml`).

### Bonsai (Blender add-on) tests
Run from `src/bonsai/`:
```
make test              # test-core + test-tool + test-bim
make test-core         # pytest -p no:pytest-blender test/core (no Blender needed)
make test-core MODULE=foo   # single core module: test/core/test_foo.py
make test-tool          # pytest test/tool
make test-tool MODULE=foo   # single: test/tool/test_foo.py
make test-bim            # pytest test/bim (needs pytest-blender)
make test-bim MODULE=foo    # filtered via -m "foo" --maxfail=1
make test-modal          # blender --enable-event-simulate ... test/modal/test_modal.py
```
`test-core` and `test-tool` run under plain pytest; `test-bim` and `test-modal` need a Blender
environment (`pytest-blender` / an actual `blender` binary).

## Architecture

This is a monorepo for the IfcOpenShell ecosystem (IFC = Industry Foundation Classes, the
building-industry BIM data format). The pieces relevant to most day-to-day work:

- `src/ifcparse/`, `src/ifcgeom/`, `src/serializers/` — C++ core: IFC parsing and geometry
  processing (OpenCASCADE and CGAL kernels), output serializers (glTF, Collada, SVG, ...).
- `src/ifcwrap/` — SWIG bindings exposing the C++ core to Python as
  `ifcopenshell.ifcopenshell_wrapper`.
- `src/ifcopenshell-python/ifcopenshell/` — the pure/wrapped-Python `ifcopenshell` API used by
  everything else in the repo (and published to PyPI). Schema-version-specific behavior is
  handled here; the library supports IFC2x3 TC1, IFC4 Add2 TC1, IFC4x1, IFC4x2, IFC4x3 Add2.
- `src/bonsai/` — the Blender add-on (GPL). This is the largest and most actively developed
  package. It follows a strict layered architecture inside `src/bonsai/bonsai/`:
  - **`core/`** — pure business logic ("use cases"). Functions take typed `tool.X` interfaces
    as parameters (see `bonsai/core/tool.py` for the Protocol definitions) instead of importing
    Blender or IFC APIs directly. This is what makes `core/` unit-testable without a Blender
    process (`make test-core` runs under plain pytest).
  - **`tool/`** — concrete implementations of the `core` Protocols, one module per domain (e.g.
    `tool/model.py`, `tool/autosave.py`, `tool/ifc.py`). These *do* talk to `bpy`/IFC directly.
    `tool/ifc.py`'s `Ifc` class is the central choke point for reading/writing the active IFC
    model from Blender.
  - **`bim/`** — the Blender-facing layer: operators, panels, and property groups, organized
    under `bim/module/<domain>/` (58 domain modules, e.g. `wall`, `cost`, `drawing`, `bsdd`).
    This layer wires Blender UI/operators to `core` functions via `tool` implementations.
  - Mirror this separation for new Bonsai functionality: business logic in `core/`, Blender/IFC
    side effects in `tool/`, UI/operator glue in `bim/module/<domain>/`. Tests mirror the same
    split under `src/bonsai/test/{core,tool,bim,modal}/`.
- `src/ifc4d/`, `src/ifc5d/`, `src/ifccsv/`, `src/ifcpatch/`, `src/ifcdiff/`, `src/ifcclash/`,
  `src/ifctester/`, `src/bcf/`, `src/bsdd/`, `src/ifccityjson/`, `src/ifcfm/` — smaller, mostly
  independent LGPL libraries/CLI tools built on `ifcopenshell-python`, each with their own
  PyPI package.

### Cross-cutting notes
- Many packages under `src/` are separate PyPI-published projects sharing this monorepo; check
  a package's own `pyproject.toml`/`setup.py` before assuming repo-root tooling applies.
- Several directories are git submodules (see `.gitmodules`) — e.g. `test/input`,
  `src/ifcopenshell-python/ifcopenshell/mvd`, `src/svgfill/3rdparty/svgpp`. Run
  `git submodule update --init --recursive` (or the pixi `init-submodules` task) if a submodule
  path appears empty.
- `pyproject.toml`'s `[tool.ruff]`/`[tool.black]` sections list generated/vendored code that is
  excluded from formatting/linting (e.g. `ifcopenshell/express/rules`, `express_parser.py`,
  `mvd/`, `simple_spf/`, `svgfill`, `exterior-shell-extractor`) — don't hand-fix style in those.
