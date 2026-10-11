# syntax=docker/dockerfile:1

# Local mirror of .github/workflows/test-lint.yml.
#
# `docker build` runs the workflow's steps in the same order and with the same
# pass/fail semantics: steps that are `continue-on-error` in the workflow record
# their status in /statuses and the final step aggregates them, so the image
# build fails exactly when the workflow's "Final check" would.

FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# "Action - setup node" step.
COPY --from=node:24 /usr/local/ /usr/local/

# "Action - setup uv" step.
COPY --from=ghcr.io/astral-sh/uv:0.11.27 /uv /uvx /usr/local/bin/

RUN apt-get update && apt-get install -y --no-install-recommends \
        bash ca-certificates curl git patch \
    && rm -rf /var/lib/apt/lists/*

# "Action - install python" steps. Only the minimum IfcOpenShell/Blender version
# is needed here. uv installs managed interpreters and tool shims straight into
# `PATH` rather than the default `~/.local`.
ENV UV_PYTHON_BIN_DIR=/usr/local/bin
ENV UV_TOOL_BIN_DIR=/usr/local/bin
RUN uv python install 3.11
# `setup-python` also provides a plain `python`, uv only links the versioned name.
RUN ln -sf /usr/local/bin/python3.11 /usr/local/bin/python && python --version

WORKDIR /__w/IfcOpenShell/IfcOpenShell
COPY . .

# The build context is a working tree, which on Windows is materialised with CRLF
# for tracked text files, while CI checks out LF. Normalise to what CI sees, so
# the whitespace check below measures the sources rather than the checkout.
# The list mirrors the checked extensions in `.github/scripts/check-whitespace.py`;
# `*.py` is handled by `ruff format` and `*.bat`/`*.cmd` are CRLF everywhere.
RUN set -eu; \
    for pattern in '*.cpp' '*.h' '*.i' '*.cmake' 'CMakeLists.txt' '*.yml' '*.yaml' '*.json' '*.ts' '*.js' '*.css' '*.sh'; do \
        find . -type f -name "$pattern" -exec sed -i 's/\r$//' {} +; \
    done

RUN mkdir -p /statuses
# The workflow appends to `$GITHUB_STEP_SUMMARY`; give the mirror somewhere to put it.
ENV GITHUB_STEP_SUMMARY=/statuses/step-summary.md

# "Install TypeScript dependencies" step.
RUN cd src/ts/ifcopenshell-js && npm ci

# "Install dependencies" step.
RUN cat requirements-tools.txt | xargs -L1 uv tool install

# "Check syntax errors" step. The formatter doesn't catch all syntax errors,
# so they are checked explicitly with both relevant Python versions.
RUN (python3.11 -W error -m compileall -q src/ifcopenshell-python && python3.11 -W error -m compileall -q src/bonsai) \
    && echo 0 > /statuses/syntax-errors \
    || echo 1 > /statuses/syntax-errors

# "Ruff format" step. Once for the GitHub annotations, once for the diff in the log.
RUN (poe ruff-format --check --output-format=github || true; poe ruff-format --check --diff) \
    && echo 0 > /statuses/ruff-format \
    || echo 1 > /statuses/ruff-format

# "ty check (venv setup)" step, not a `continue-on-error` step.
RUN poe ty-venv

# "ty check (bonsai)" step.
RUN poe ty-bonsai && echo 0 > /statuses/ty-bonsai || echo 1 > /statuses/ty-bonsai

# "ty check (ios)" step.
RUN poe ty-ios && echo 0 > /statuses/ty-ios || echo 1 > /statuses/ty-ios

# "Ruff check" step. `ansi2txt` keeps the colored log readable in the summary,
# and `ruff` disables color output in CI by default, hence `FORCE_COLOR`.
RUN set +e; \
    ERROR=0; \
    uv tool install ansi2txt; \
    export FORCE_COLOR="1"; \
    out="$(poe ruff 2>&1)"; \
    if [ $? -ne 0 ]; then ERROR=1; fi; \
    poe ruff --output-format=github || true; \
    echo "$out"; \
    { echo '```python'; echo "$out" | ansi2txt; echo '```'; } >> "$GITHUB_STEP_SUMMARY"; \
    echo "$ERROR" > /statuses/ruff

# "Check whitespace" step.
RUN poe check-whitespace --check && echo 0 > /statuses/check-whitespace || echo 1 > /statuses/check-whitespace

# "ESLint (TypeScript)" step.
RUN cd src/ts/ifcopenshell-js && npm run lint && echo 0 > /statuses/ts-eslint || echo 1 > /statuses/ts-eslint

# "Check TypeScript whitespace" step.
RUN uv run .github/scripts/check-whitespace.py src/ts/ifcopenshell-js/src --check \
    && echo 0 > /statuses/ts-whitespace \
    || echo 1 > /statuses/ts-whitespace

# "Final check" step. Mirrors the workflow's aggregation of the
# `continue-on-error` steps, so the image build fails exactly when it would.
RUN ERROR=0; \
    for step in syntax-errors ruff-format ty-bonsai ty-ios ruff check-whitespace ts-eslint ts-whitespace; do \
        if [ "$(cat "/statuses/$step")" != "0" ]; then \
            echo "::error::Step '$step' failed, see the corresponding layer in the build log for the details."; \
            ERROR=1; \
        fi; \
    done; \
    exit $ERROR
