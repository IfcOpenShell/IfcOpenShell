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

"""Shared post-disconnect cleanup dispatch.

Used by both ``bim.disconnect_elements`` (explicit user disconnect) and the
connection cascade in ``tool.Geometry.delete_ifc_object`` (implicit
disconnect-on-delete). Each kind returned by
:py:meth:`bonsai.tool.connection.Connection.find_rels` /
:py:meth:`find_rels_for_element` maps to a single arm here, so adding a new
kind means extending one dispatch table — both call sites benefit
automatically and the AST forward-compat guard enforces coverage.

The ``subject`` parameter is the entity whose teardown effects the
disconnect: for ``"path"`` / ``"element"`` / ``"element-top"`` kinds it
carries an ``IfcRel*`` relationship entity (the rel that gets removed);
for ``"mep-pair-fitting"`` it carries an ``IfcFlowFitting`` (the fitting
that gets deleted). The slot is uniform on intent — the dispatch decides
the teardown mechanism by kind.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import bonsai.core.geometry
from bonsai.core.model import regenerate_wall_to_underside

if TYPE_CHECKING:
    import ifcopenshell

    import bonsai.tool as tool


def disconnect_rel(
    ifc: type[tool.Ifc],
    geometry: type[tool.Geometry],
    model: type[tool.Model],
    connection: type[tool.Connection],
    subject: ifcopenshell.entity_instance,
    kind: str,
    elem: ifcopenshell.entity_instance,
    partner: ifcopenshell.entity_instance,
    skip_elem_recreate: bool = False,
    skip_partner_recreate: bool = False,
) -> None:
    """Run the post-disconnect cleanup for one connection.

    ``elem`` and ``partner`` are the two endpoints. The ``skip_*_recreate``
    flags suppress per-side regenerate / recreate work — used by the
    cascade-on-delete to avoid re-extruding entities that are about to be
    removed by ``remove_product``. For the disconnect operator (where neither
    endpoint is being deleted), both flags stay False and the full cleanup
    runs on both sides.
    """
    if kind == "path":
        bonsai.core.geometry.remove_connection(geometry, connection=subject)
        if not skip_elem_recreate:
            elem_obj = ifc.get_object(elem)
            if elem_obj is not None:
                model.recreate_wall(elem, elem_obj)
        if not skip_partner_recreate:
            partner_obj = ifc.get_object(partner)
            if partner_obj is not None:
                model.recreate_wall(partner, partner_obj)
    elif kind == "element-top":
        wall, _slab = connection.orient_element_top(subject, elem, partner)
        ifc.run(
            "geometry.disconnect_element",
            relating_element=subject.RelatingElement,
            related_element=subject.RelatedElement,
        )
        # Skip the wall-side regenerate when the wall is itself being deleted —
        # either it's the elem of this cascade pass, or it's the partner that
        # was queued earlier in the same batch.
        if (wall is elem and skip_elem_recreate) or (wall is partner and skip_partner_recreate):
            return
        wall_obj = ifc.get_object(wall)
        if wall_obj is not None:
            regenerate_wall_to_underside(ifc, geometry, model, [wall_obj])
    elif kind == "element":
        ifc.run(
            "geometry.disconnect_element",
            relating_element=subject.RelatingElement,
            related_element=subject.RelatedElement,
        )
    elif kind == "mep-pair-fitting":
        if skip_elem_recreate and subject is elem:
            return
        if skip_partner_recreate and subject is partner:
            return
        fitting_obj = ifc.get_object(subject)
        if fitting_obj is not None:
            geometry.delete_ifc_object(fitting_obj)
    else:
        raise ValueError(f"Unknown kind: {kind!r}")
