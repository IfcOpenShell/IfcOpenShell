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

"""Generic discovery of the connection linking two IFC elements.

Used by ``bim.disconnect_elements`` so the operator surface is one operator
per disconnect intent (active vs. partner, identified by GlobalId) rather
than one per rel class. Each lookup returns ``(subject, kind)`` tuples where
``subject`` is the entity whose teardown effects the disconnect:

- ``"path"`` — ``IfcRelConnectsPathElements`` (wall-wall, wall-roof, etc.).
  ``subject`` is the rel; removing it disconnects.
- ``"element-top"`` — ``IfcRelConnectsElements`` with ``Description=="TOP"``
  (created by ``extend_walls_to_underside``). ``subject`` is the rel.
- ``"element"`` — any other ``IfcRelConnectsElements``. ``subject`` is the rel.
- ``"mep-pair-fitting"`` — two MEP elements joined via ``IfcRelConnectsPorts``
  through a single bridging ``IfcFlowFitting``. ``subject`` is the fitting
  itself; removing it disconnects. ``OBSTRUCTION`` fittings are excluded
  here; those go through ``bim.mep_add_obstruction(mode=REMOVE)``.

Add new kinds by extending :py:meth:`Connection.find_rels`. The dispatch in
``bonsai.core.connection.disconnect_rel`` maps each kind to the right
post-mutation cleanup; the AST forward-compat guard enforces coverage."""

from __future__ import annotations

from typing import TYPE_CHECKING

import bonsai.tool as tool

if TYPE_CHECKING:
    import ifcopenshell


class Connection:
    @classmethod
    def find_rels(
        cls,
        elem_a: ifcopenshell.entity_instance,
        elem_b: ifcopenshell.entity_instance,
    ) -> list[tuple[ifcopenshell.entity_instance, str]]:
        """Return every supported connection linking ``elem_a`` to ``elem_b``
        as a list of ``(subject, kind)`` tuples — ``subject`` is the entity
        whose teardown effects the disconnect (the rel itself for
        relationship-kinds, the bridging fitting for ``"mep-pair-fitting"``).
        Walks both ``ConnectedTo`` and ``ConnectedFrom`` because either side
        of a rel can be the relating element, and the same pair may carry
        rels authored with opposite orientations."""
        rels: list[tuple[ifcopenshell.entity_instance, str]] = []
        seen: set[int] = set()

        def _record(rel, kind):
            if rel.id() not in seen:
                seen.add(rel.id())
                rels.append((rel, kind))

        for rel in getattr(elem_a, "ConnectedTo", []) or ():
            if rel.is_a("IfcRelConnectsPathElements") and getattr(rel, "RelatedElement", None) == elem_b:
                _record(rel, "path")
        for rel in getattr(elem_a, "ConnectedFrom", []) or ():
            if rel.is_a("IfcRelConnectsPathElements") and getattr(rel, "RelatingElement", None) == elem_b:
                _record(rel, "path")

        for rel in getattr(elem_a, "ConnectedFrom", []) or ():
            if rel.is_a("IfcRelConnectsElements") and getattr(rel, "RelatingElement", None) == elem_b:
                kind = "element-top" if getattr(rel, "Description", None) == "TOP" else "element"
                _record(rel, kind)
        for rel in getattr(elem_a, "ConnectedTo", []) or ():
            if rel.is_a("IfcRelConnectsElements") and getattr(rel, "RelatedElement", None) == elem_b:
                kind = "element-top" if getattr(rel, "Description", None) == "TOP" else "element"
                _record(rel, kind)

        fitting = tool.System.find_bridging_fitting(elem_a, elem_b)
        if fitting is not None:
            _record(fitting, "mep-pair-fitting")

        return rels

    @classmethod
    def find_rel(
        cls,
        elem_a: ifcopenshell.entity_instance,
        elem_b: ifcopenshell.entity_instance,
    ) -> tuple[ifcopenshell.entity_instance | None, str | None]:
        """Return the first ``(subject, kind)`` or ``(None, None)``. Cheaper
        than ``find_rels`` when callers only need to know whether a connection
        exists or what kind it is."""
        rels = cls.find_rels(elem_a, elem_b)
        return rels[0] if rels else (None, None)

    @classmethod
    def find_rels_for_element(
        cls,
        elem: ifcopenshell.entity_instance,
    ) -> list[tuple[ifcopenshell.entity_instance, str, ifcopenshell.entity_instance]]:
        """Return every supported connection touching ``elem`` as
        ``(subject, kind, partner)`` triples. ``partner`` is the *other*
        element on the connection — the side cascade cleanup must operate on
        when ``elem`` is being deleted.

        Mirrors :py:meth:`find_rels`'s relationship-kind taxonomy. Notably
        does NOT emit ``"mep-pair-fitting"`` triples: ``IfcRelConnectsPorts``
        cleanup is owned by ``tool.Geometry.delete_ifc_object``'s
        ``remove_port`` loop, which runs unconditionally on any IFC root
        deletion. Including MEP here would cause the cascade to also remove
        the bridging fitting when one of its connected segments is deleted —
        a policy choice (fitting may still join other live segments) that's
        better left to the user via the explicit disconnect operator.
        """
        result: list[tuple[ifcopenshell.entity_instance, str, ifcopenshell.entity_instance]] = []
        seen: set[int] = set()

        def _record(rel, kind, partner):
            if partner is None or rel.id() in seen:
                return
            seen.add(rel.id())
            result.append((rel, kind, partner))

        for rel in getattr(elem, "ConnectedTo", []) or ():
            if rel.is_a("IfcRelConnectsPathElements"):
                _record(rel, "path", getattr(rel, "RelatedElement", None))
            elif rel.is_a("IfcRelConnectsElements"):
                kind = "element-top" if getattr(rel, "Description", None) == "TOP" else "element"
                _record(rel, kind, getattr(rel, "RelatedElement", None))
        for rel in getattr(elem, "ConnectedFrom", []) or ():
            if rel.is_a("IfcRelConnectsPathElements"):
                _record(rel, "path", getattr(rel, "RelatingElement", None))
            elif rel.is_a("IfcRelConnectsElements"):
                kind = "element-top" if getattr(rel, "Description", None) == "TOP" else "element"
                _record(rel, kind, getattr(rel, "RelatingElement", None))

        return result

    @classmethod
    def orient_element_top(
        cls,
        rel: ifcopenshell.entity_instance,
        elem_a: ifcopenshell.entity_instance,
        elem_b: ifcopenshell.entity_instance,
    ) -> tuple[ifcopenshell.entity_instance, ifcopenshell.entity_instance]:
        """Return ``(wall, slab)`` for an ``IfcRelConnectsElements(TOP)`` rel.

        The ``extend_walls_to_underside`` flow stores slab as the relating
        side and wall as related — orientation is recovered by checking
        which input matches which rel attribute. Callers pass any two
        elements; this resolves which is the wall and which is the slab so
        post-disconnect cleanup (regenerate-wall-to-underside) targets the
        right object."""
        if getattr(rel, "RelatingElement", None) == elem_a:
            return elem_b, elem_a
        return elem_a, elem_b
