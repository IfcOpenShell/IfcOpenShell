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

"""Forward-compat AST contracts for wall gizmo internals.

Pins structural invariants that no per-call-site behavioural test can catch
on its own: the kind of "someone tidied the imports" regression that leaves
tests green but silently changes runtime semantics. Each contract names the
invariant it pins so a future revert tells the contributor exactly what the
rule is."""

import ast
import inspect

import pytest

pytestmark = pytest.mark.wall


def test_iter_path_connections_uses_path_connectable_predicate():
    """The partner filter must consult the looser ``is_path_connectable_wall``
    predicate, matching the host-side predicate used by the gizmo group's
    poll. Strict ``is_wall`` rejects fillet-corner walls (which have no
    LAYER2 usage by IFC spec), so a regression to ``is_wall`` would silently
    drop fillet partners from the connection list — visible to the user as
    "the corner looks unconnected from the adjacent wall's selection.\""""
    from bonsai.bim.module.model.wall import _iter_path_connections

    source = inspect.getsource(_iter_path_connections)
    tree = ast.parse(source)
    attr_names = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}

    assert "is_path_connectable_wall" in attr_names, (
        "_iter_path_connections must filter partners with is_path_connectable_wall — "
        "the same predicate the gizmo group's poll uses on the host wall. "
        "Symmetry between host and partner predicates is required for fillet "
        "corners (no LAYER2 usage) to surface as connected from their LAYER2 "
        "neighbours' perspective."
    )
    assert "is_wall" not in attr_names, (
        "_iter_path_connections must NOT call .is_wall on partner elements — "
        "that strict predicate drops fillet-corner walls. Use "
        "is_path_connectable_wall instead."
    )
