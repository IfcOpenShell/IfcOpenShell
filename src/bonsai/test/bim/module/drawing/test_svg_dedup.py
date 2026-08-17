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

"""Tests for svg_dedup.merge_duplicate_edges() (known-issues item 21).

svg_dedup.py has no bpy dependency, so these run as plain pytest -- no
Blender required. It's loaded directly by file path rather than via
``from bonsai.bim.module.drawing.svg_dedup import ...`` because importing
*any* submodule of the ``bonsai.bim`` package first runs
``bonsai/bim/__init__.py``, which does ``import bpy`` unconditionally."""

import importlib.util
from pathlib import Path

import pytest
from lxml import etree

_svg_dedup_path = Path(__file__).parents[4] / "bonsai" / "bim" / "module" / "drawing" / "svg_dedup.py"
_spec = importlib.util.spec_from_file_location("svg_dedup", _svg_dedup_path)
svg_dedup = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(svg_dedup)
merge_duplicate_edges = svg_dedup.merge_duplicate_edges

SVG_NS = "http://www.w3.org/2000/svg"
IFC_NS = "http://www.ifcopenshell.org/ns"
NSMAP = {"svg": SVG_NS, "ifc": IFC_NS}


def _build_root(products: dict) -> "etree._Element":
    """products: {guid: [(d, class), ...]} -> one <g ifc:guid> per product,
    one <path> per (d, class) entry, matching the real serializer's own
    per-product <g> nesting."""
    root = etree.Element(f"{{{SVG_NS}}}svg", nsmap={None: SVG_NS, "ifc": IFC_NS})
    top_group = etree.SubElement(root, f"{{{SVG_NS}}}g")
    for guid, paths in products.items():
        g = etree.SubElement(top_group, f"{{{SVG_NS}}}g")
        g.set(f"{{{IFC_NS}}}guid", guid)
        for d, cls in paths:
            path = etree.SubElement(g, f"{{{SVG_NS}}}path")
            path.set("d", d)
            path.set("class", cls)
    return root


def _paths_by_guid(root) -> dict:
    result = {}
    for g in root.findall(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid]"):
        guid = g.get(f"{{{IFC_NS}}}guid")
        result[guid] = [(p.get("d"), p.get("class")) for p in g.findall(f"{{{SVG_NS}}}path")]
    return result


def test_exact_duplicate_across_products_is_removed():
    root = _build_root(
        {
            "A": [("M0,0 L10,0", "cross-coplanar")],
            "B": [("M0,0 L10,0", "cross-coplanar")],
        }
    )

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    total_paths = sum(len(v) for v in remaining.values())
    assert total_paths == 1
    # The surviving path is still under one of the two real product <g>s.
    assert (remaining["A"] == [] and remaining["B"] == [("M0,0 L10,0", "cross-coplanar")]) or (
        remaining["B"] == [] and remaining["A"] == [("M0,0 L10,0", "cross-coplanar")]
    )


def test_partial_overlap_trims_the_shorter_edge_in_place():
    # A spans 0..7 (the longer, surviving-whole path). B spans 4..10, overlapping
    # A over 4..7 but extending 3 units further. B's own path must be trimmed
    # down to just its own non-overlapping remainder (~7..10), not deleted, and
    # must stay under B's own <g>.
    root = _build_root(
        {
            "A": [("M0,0 L7,0", "outline")],
            "B": [("M4,0 L10,0", "outline")],
        }
    )

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L7,0", "outline")]
    assert len(remaining["B"]) == 1
    d, cls = remaining["B"][0]
    assert cls == "outline"
    coords = [tuple(float(v) for v in pt.split(",")) for pt in d.replace("M", "").replace("L", "").split()]
    # Small buffer tolerance in the trim means the remainder's start creeps a
    # touch past 7, not exactly on it -- assert closeness, not equality.
    assert coords[0][0] == pytest.approx(7.0, abs=0.01)
    assert coords[0][1] == pytest.approx(0.0, abs=0.01)
    assert coords[-1] == (10.0, 0.0)


def test_disjoint_same_class_edges_are_left_untouched():
    root = _build_root(
        {
            "A": [("M0,0 L10,0", "sharp")],
            "B": [("M20,0 L30,0", "sharp")],
        }
    )

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L10,0", "sharp")]
    assert remaining["B"] == [("M20,0 L30,0", "sharp")]


def test_crossing_edges_are_not_treated_as_overlapping():
    # These two lines cross at a single point (5,5) -- not collinear overlap --
    # and must both survive untouched.
    root = _build_root(
        {
            "A": [("M0,0 L10,10", "sharp")],
            "B": [("M0,10 L10,0", "sharp")],
        }
    )

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L10,10", "sharp")]
    assert remaining["B"] == [("M0,10 L10,0", "sharp")]


def test_different_classes_are_never_merged():
    # Same physical line, different classification -- existing cross-class
    # dedup in SvgSerializer.cpp already handles this deliberately elsewhere;
    # this pass must not touch cross-class pairs at all.
    root = _build_root(
        {
            "A": [("M0,0 L10,0", "outline")],
            "B": [("M0,0 L10,0", "boundary")],
        }
    )

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L10,0", "outline")]
    assert remaining["B"] == [("M0,0 L10,0", "boundary")]


def test_unclassified_and_closed_polygon_paths_are_ignored():
    # No class attribute (e.g. a merged polygon-fill path from
    # merge_linework_and_add_metadata()'s own earlier phase) must be skipped
    # entirely, not crash the class-keyed grouping.
    root = _build_root({"A": [("M0,0 L10,0 L10,10 Z", "")]})
    a_group = root.find(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid='A']")
    a_group[0].attrib.pop("class")

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L10,0 L10,10 Z", None)]


def test_cut_and_projection_duplicates_are_never_cross_merged():
    # Known-issues item 52: operator.py's SHAPELY fill-boundary scan only ever
    # looks at "projection"-classed groups (matches merge_linework_and_add_
    # metadata()'s own real convention: the guid-<g> itself carries a "cut" or
    # "projection" token alongside its other classes). A's own copy is longer
    # (so, pre-fix, it would win as _resolve_cluster()'s survivor purely by
    # length and delete B's shorter "projection" copy) -- but A is "cut" and B
    # is "projection", so they must never cluster together at all: both must
    # survive fully intact.
    root = _build_root(
        {
            "A": [("M0,0 L10,0", "outline")],
            "B": [("M0,0 L8,0", "outline")],
        }
    )
    a_group = root.find(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid='A']")
    b_group = root.find(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid='B']")
    a_group.set("class", "IfcWall cut")
    b_group.set("class", "IfcWall projection")

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    assert remaining["A"] == [("M0,0 L10,0", "outline")]
    assert remaining["B"] == [("M0,0 L8,0", "outline")]


def test_same_group_kind_duplicates_still_merge_across_products():
    # Companion to the test above: two "projection"-classed products with a
    # genuine duplicate must still dedup exactly as before -- item 52's fix
    # only scopes clustering apart across cut/projection, not within one kind.
    root = _build_root(
        {
            "A": [("M0,0 L10,0", "outline")],
            "B": [("M0,0 L10,0", "outline")],
        }
    )
    a_group = root.find(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid='A']")
    b_group = root.find(f".//{{{SVG_NS}}}g[@{{{IFC_NS}}}guid='B']")
    a_group.set("class", "IfcWall projection")
    b_group.set("class", "IfcSlab projection")

    merge_duplicate_edges(root)

    remaining = _paths_by_guid(root)
    total_paths = sum(len(v) for v in remaining.values())
    assert total_paths == 1
