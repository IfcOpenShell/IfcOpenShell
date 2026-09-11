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
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.
#
# This file was generated with the assistance of an AI coding tool.

"""Regression test for #5622: unassigning a type from an occurrence must not
drop the presentation styles the occurrence displayed through the type's
mapped representation.

``UnassignType.unassign_and_unmap`` (bonsai/bim/module/type/operator.py)
bakes a private copy of any mapped representation onto the occurrence via
``ifcopenshell.util.element.copy_deep`` before severing the type link.
``copy_deep`` only follows *forward* attributes, and ``IfcStyledItem`` is only
reachable through the *inverse* ``StyledByItem``, so a naive copy silently
drops the occurrence's inherited surface styles. ``_reattach_styles``
re-creates an ``IfcStyledItem`` on each copied item to close that gap.
"""

import pytest

pytestmark = pytest.mark.type


@pytest.fixture(autouse=True)
def _require_real_bpy():
    import types as _types

    import bpy

    if not isinstance(bpy, _types.ModuleType) or hasattr(bpy, "_mock_name"):
        pytest.skip("requires real Blender (bpy is mocked or absent)")


@pytest.fixture
def fresh_ifc():
    import ifcopenshell

    from bonsai.bim.ifc import IfcStore

    previous = IfcStore.file
    IfcStore.file = ifcopenshell.file(schema="IFC4")
    try:
        yield IfcStore.file
    finally:
        IfcStore.file = previous


def _add_context(ifc_file):
    import ifcopenshell.api.context
    import ifcopenshell.api.root

    if not ifc_file.by_type("IfcProject"):
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="P")

    model_context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")
    return ifcopenshell.api.context.add_context(
        ifc_file,
        context_type="Model",
        context_identifier="Body",
        target_view="MODEL_VIEW",
        parent=model_context,
    )


def _add_box_shape(ifc_file, body_context, x=1.0):
    point_list = ifc_file.create_entity(
        "IfcCartesianPointList3D",
        CoordList=[(0.0, 0.0, 0.0), (x, 0.0, 0.0), (x, x, 0.0), (0.0, x, 0.0)],
    )
    face = ifc_file.create_entity("IfcIndexedPolygonalFace", CoordIndex=(1, 2, 3, 4))
    shell = ifc_file.create_entity("IfcPolygonalFaceSet", Coordinates=point_list, Faces=[face])
    shape_rep = ifc_file.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=body_context,
        RepresentationIdentifier="Body",
        RepresentationType="Tessellation",
        Items=[shell],
    )
    return shape_rep, shell


def _assign_red_style(ifc_file, item):
    import ifcopenshell.api.style

    style = ifcopenshell.api.style.add_style(ifc_file, name="Red")
    ifcopenshell.api.style.add_surface_style(
        ifc_file,
        style=style,
        ifc_class="IfcSurfaceStyleShading",
        attributes={"SurfaceColour": {"Red": 1.0, "Green": 0.0, "Blue": 0.0}},
    )
    ifc_file.create_entity("IfcStyledItem", Item=item, Styles=[style], Name=None)
    return style


def _make_linked_object(name, element):
    """Build a real bpy.types.Object + mesh, linked to an IFC entity via
    tool.Ifc.link, with the mesh's tracked representation id set so
    tool.Geometry.get_active_representation(obj) resolves it."""
    import bpy

    import bonsai.tool as tool

    mesh = bpy.data.meshes.new(name)
    obj = bpy.data.objects.new(name, mesh)
    tool.Ifc.link(element, obj)
    return obj


def _get_styles_on_body(element):
    import ifcopenshell.util.representation

    styles = set()
    if not element.Representation:
        return styles
    for rep in element.Representation.Representations:
        resolved = ifcopenshell.util.representation.resolve_representation(rep)
        for item in resolved.Items:
            for styled_item in getattr(item, "StyledByItem", None) or []:
                for style in styled_item.Styles:
                    styles.add(style.id())
    return styles


def _make_typed_wall(fresh_ifc, body_context):
    import ifcopenshell.api.root
    import ifcopenshell.api.type

    type_shape, type_item = _add_box_shape(fresh_ifc, body_context)
    style = _assign_red_style(fresh_ifc, type_item)

    wall_type = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWallType", name="WallType")
    rep_map = fresh_ifc.create_entity(
        "IfcRepresentationMap",
        MappingOrigin=fresh_ifc.create_entity(
            "IfcAxis2Placement3D",
            Location=fresh_ifc.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        ),
        MappedRepresentation=type_shape,
    )
    wall_type.RepresentationMaps = [rep_map]

    wall = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWall", name="Wall")
    ifcopenshell.api.type.assign_type(fresh_ifc, related_objects=[wall], relating_type=wall_type)
    return wall, wall_type, style


def test_unassign_type_retains_style_from_mapped_representation(fresh_ifc):
    """The bug in #5622: unassigning a type used to leave the occurrence
    with an unmapped copy of the geometry but no styles."""
    import ifcopenshell.util.element
    import ifcopenshell.util.representation

    from bonsai.bim.module.type.operator import UnassignType

    body_context = _add_context(fresh_ifc)
    wall, wall_type, style = _make_typed_wall(fresh_ifc, body_context)
    wall_obj = _make_linked_object("Wall", wall)

    body_rep = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
    resolved_body_rep = ifcopenshell.util.representation.resolve_representation(body_rep)
    wall_obj.data.BIMMeshProperties.ifc_definition_id = resolved_body_rep.id()

    styles_before = _get_styles_on_body(wall)
    assert style.id() in styles_before, "sanity check: wall should show the type's style before unassign"

    UnassignType.unassign_and_unmap(wall_obj)

    assert ifcopenshell.util.element.get_type(wall) is None, "type must be unassigned"
    for rep in wall.Representation.Representations:
        assert (
            ifcopenshell.util.representation.resolve_representation(rep) == rep
        ), "representation should be a private (unmapped) copy after unassign"

    styles_after = _get_styles_on_body(wall)
    assert style.id() in styles_after, (
        "the wall lost its style after unassigning the type -- #5622 regression "
        f"(styles_before={styles_before}, styles_after={styles_after})"
    )


def test_unassign_type_leaves_instance_owned_style_untouched(fresh_ifc):
    """A representation the occurrence owns directly (not mapped from a
    type) never goes through copy_deep, so its style must survive
    unassign_type unmodified, whether or not a type was even assigned."""
    import ifcopenshell.api.geometry
    import ifcopenshell.api.root

    from bonsai.bim.module.type.operator import UnassignType

    body_context = _add_context(fresh_ifc)
    wall = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWall", name="Wall")
    own_shape, own_item = _add_box_shape(fresh_ifc, body_context, x=2.0)
    ifcopenshell.api.geometry.assign_representation(fresh_ifc, product=wall, representation=own_shape)
    style = _assign_red_style(fresh_ifc, own_item)

    wall_obj = _make_linked_object("Wall", wall)
    wall_obj.data.BIMMeshProperties.ifc_definition_id = own_shape.id()

    styles_before = _get_styles_on_body(wall)
    assert style.id() in styles_before

    UnassignType.unassign_and_unmap(wall_obj)  # no type assigned: should be a no-op

    styles_after = _get_styles_on_body(wall)
    assert styles_after == styles_before, "instance-owned style must be unaffected by unassign_type"


def test_unassign_type_with_no_styles_does_not_error(fresh_ifc):
    """A type whose mapped representation has no styles at all must unassign
    cleanly (no exception), leaving the occurrence with no styles."""
    import ifcopenshell.api.root
    import ifcopenshell.api.type

    from bonsai.bim.module.type.operator import UnassignType

    body_context = _add_context(fresh_ifc)
    type_shape, type_item = _add_box_shape(fresh_ifc, body_context)  # no style assigned

    wall_type = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWallType", name="WallType")
    rep_map = fresh_ifc.create_entity(
        "IfcRepresentationMap",
        MappingOrigin=fresh_ifc.create_entity(
            "IfcAxis2Placement3D",
            Location=fresh_ifc.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
        ),
        MappedRepresentation=type_shape,
    )
    wall_type.RepresentationMaps = [rep_map]

    wall = ifcopenshell.api.root.create_entity(fresh_ifc, ifc_class="IfcWall", name="Wall")
    ifcopenshell.api.type.assign_type(fresh_ifc, related_objects=[wall], relating_type=wall_type)
    wall_obj = _make_linked_object("Wall", wall)

    import ifcopenshell.util.representation

    body_rep = ifcopenshell.util.representation.get_representation(wall, "Model", "Body", "MODEL_VIEW")
    resolved_body_rep = ifcopenshell.util.representation.resolve_representation(body_rep)
    wall_obj.data.BIMMeshProperties.ifc_definition_id = resolved_body_rep.id()

    UnassignType.unassign_and_unmap(wall_obj)  # must not raise

    assert _get_styles_on_body(wall) == set()
