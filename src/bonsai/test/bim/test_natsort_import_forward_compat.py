# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2026
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Forward-compat AST contract for the optional ``natsort`` dependency.

``natsorted`` is only used for cosmetic natural-sort ordering of UI dropdown
and enum lists (see #6900). A bare module-level ``from natsort import
natsorted`` makes ALL of Bonsai's addon registration hostage to natsort:
if natsort is missing, or left partially initialized by some unrelated
package colliding on ``sys.path`` (e.g. Sverchok's Conda "Python Path"
feature dropping a `.pth` file), the resulting ``ImportError``/
``AttributeError`` propagates out of ``bonsai.bim``'s module-level imports
and silently disables the whole addon, not just natural sorting.

Every module-level natsort import must therefore be guarded by a
``try/except`` that falls back to the stdlib ``sorted()``."""

import ast
from pathlib import Path

import pytest

pytestmark = pytest.mark.contract_guard

ADDON_ROOT = Path(__file__).parent.parent.parent / "bonsai"


def _is_natsort_import(node: ast.stmt) -> bool:
    if isinstance(node, ast.ImportFrom):
        return node.module == "natsort"
    if isinstance(node, ast.Import):
        return any(alias.name == "natsort" or alias.name.startswith("natsort.") for alias in node.names)
    return False


def _try_guards_natsort(node: ast.Try) -> bool:
    has_import = any(_is_natsort_import(stmt) for stmt in node.body)
    return has_import and bool(node.handlers)


def test_no_module_level_natsort_import_is_unguarded() -> None:
    offenders: list[str] = []
    for path in sorted(ADDON_ROOT.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        for node in tree.body:  # module-level statements only
            if isinstance(node, ast.Try):
                if any(_is_natsort_import(stmt) for stmt in node.body) and not _try_guards_natsort(node):
                    rel = path.relative_to(ADDON_ROOT)
                    offenders.append(f"{rel.as_posix()}:{node.lineno}: try-block imports natsort without except")
                continue
            if _is_natsort_import(node):
                rel = path.relative_to(ADDON_ROOT)
                offenders.append(f"{rel.as_posix()}:{node.lineno}: unguarded module-level natsort import")
    if offenders:
        listing = "\n  ".join(offenders)
        pytest.fail(
            "Unguarded module-level natsort import(s) found. Wrap in "
            "`try: from natsort import natsorted\\nexcept Exception: natsorted = sorted` "
            "so a missing/broken natsort degrades to plain sort() instead of disabling all "
            "of Bonsai:\n  " + listing
        )
