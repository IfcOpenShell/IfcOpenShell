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

"""Guards ``bim.mirror_elements`` against mirroring shared type geometry.

When a typed occurrence's body is an ``IfcMappedItem``, the mapped
representation belongs to the type and is shared with every sibling
occurrence. Inverting it in place would silently mirror the whole family.
``MirrorElements`` must refuse that and route such occurrences through
``assign_inverted_type`` instead, which mirrors a private copy of the type.

Also pins the single-axis rule in ``get_mirror_axes``: flipping two local
axes at once is a 180 degree rotation, not a reflection, and would leave
``reflect_placement`` composing two determinant +1 matrices."""

from types import SimpleNamespace
from unittest.mock import patch

import ifcopenshell
import numpy as np
import pytest
from mathutils import Matrix, Vector

pytestmark = pytest.mark.model


def _mapped_type_file():
    """An IFC4 file with one type carrying a triangle, mapped by two occurrences."""
    f = ifcopenshell.file(schema="IFC4")
    context = f.create_entity(
        "IfcGeometricRepresentationContext",
        ContextType="Model",
        CoordinateSpaceDimension=3,
        WorldCoordinateSystem=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
    )
    points = [f.create_entity("IfcCartesianPoint", Coordinates=c) for c in ((0.0, 0.0), (3.0, 0.0), (0.5, 1.0))]
    profile = f.create_entity(
        "IfcArbitraryClosedProfileDef",
        ProfileType="AREA",
        OuterCurve=f.create_entity("IfcPolyline", Points=points + [points[0]]),
    )
    solid = f.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=profile,
        Position=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
        ExtrudedDirection=f.create_entity("IfcDirection", DirectionRatios=(0.0, 0.0, 1.0)),
        Depth=1.0,
    )
    mapped_representation = f.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=context,
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid],
    )
    representation_map = f.create_entity(
        "IfcRepresentationMap",
        MappingOrigin=f.create_entity(
            "IfcAxis2Placement3D", Location=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0))
        ),
        MappedRepresentation=mapped_representation,
    )
    element_type = f.create_entity("IfcFurnitureType", GlobalId="0" * 22, RepresentationMaps=[representation_map])

    occurrences = []
    for _ in range(2):
        target = f.create_entity(
            "IfcCartesianTransformationOperator3D",
            LocalOrigin=f.create_entity("IfcCartesianPoint", Coordinates=(0.0, 0.0, 0.0)),
            Scale=1.0,
        )
        mapped_item = f.create_entity("IfcMappedItem", MappingSource=representation_map, MappingTarget=target)
        occurrence = f.create_entity(
            "IfcFurniture",
            GlobalId="1" * 22,
            Representation=f.create_entity(
                "IfcProductDefinitionShape",
                Representations=[
                    f.create_entity(
                        "IfcShapeRepresentation",
                        ContextOfItems=context,
                        RepresentationIdentifier="Body",
                        RepresentationType="MappedRepresentation",
                        Items=[mapped_item],
                    )
                ],
            ),
        )
        occurrences.append(occurrence)
    return f, element_type, occurrences, solid


def _profile_coordinates(solid):
    return [tuple(p.Coordinates) for p in solid.SweptArea.OuterCurve.Points]


def _operator():
    """A plain stand-in carrying the operator's methods.

    ``bpy.types.Operator`` subclasses cannot be instantiated outside an operator
    call, and none of the methods under test need operator state beyond
    ``unsupported_items``."""
    from bonsai.bim.module.model.product import MirrorElements

    methods = (
        "find_uninvertible_items",
        "get_mirror_axes",
        "invert_general_object",
        "invert_representation",
        "get_mirror_plane_point",
        "is_type_owned_mapping",
        "reflect_placement",
    )
    # __dict__ rather than getattr so staticmethod descriptors survive the copy
    stub = type("MirrorElementsStub", (), {name: MirrorElements.__dict__[name] for name in methods})()
    stub.unsupported_items = set()
    return stub


def test_mirroring_a_mapped_occurrence_leaves_the_shared_type_untouched():
    from bonsai.bim.module.model.product import SharedMappedGeometryError

    ifc_file, _, occurrences, solid = _mapped_type_file()
    coordinates_before = _profile_coordinates(solid)
    operator = _operator()

    with patch("bonsai.tool.Ifc.get", return_value=ifc_file):
        with pytest.raises(SharedMappedGeometryError):
            operator.invert_general_object(occurrences[0])

    assert _profile_coordinates(solid) == coordinates_before


def test_a_privately_mapped_representation_is_still_mirrored():
    """A mapping used by a single occurrence and owned by no type is safe to invert."""
    ifc_file, element_type, occurrences, solid = _mapped_type_file()
    # Detach the type and the second occurrence so only one IfcMappedItem is left.
    ifc_file.remove(occurrences[1].Representation.Representations[0].Items[0])
    element_type.RepresentationMaps = None
    representation_map = occurrences[0].Representation.Representations[0].Items[0].MappingSource

    operator = _operator()
    coordinates_before = _profile_coordinates(solid)
    with patch("bonsai.tool.Ifc.get", return_value=ifc_file):
        assert len(representation_map.MapUsage) == 1
        assert operator.is_type_owned_mapping(occurrences[0].Representation.Representations[0].Items[0]) is False
        with patch("bonsai.tool.Ifc.get_object", return_value=None):
            with patch("bonsai.tool.Geometry.reload_representation"):
                operator.invert_general_object(occurrences[0], (1.0, 0.0, 0.0))

    coordinates_after = _profile_coordinates(solid)
    assert coordinates_after != coordinates_before
    assert [round(-x, 6) for x, _ in coordinates_before] == [round(x, 6) for x, _ in coordinates_after]


def test_reflect_placement_across_a_reference_is_an_exact_reflection():
    """The placement maths, independent of IFC: a point must land at its mirror image."""
    operator = _operator()
    obj = SimpleNamespace(matrix_world=Matrix.Translation((2.0, 0.0, 0.0)), location=None)
    # bound_box all zeros, as for an empty, so the plane passes through the reference origin
    reference = SimpleNamespace(matrix_world=Matrix.Translation((5.0, 0.0, 0.0)), bound_box=[(0.0, 0.0, 0.0)] * 8)
    operator.reflect_placement(obj, reference, (1.0, 0.0, 0.0), {}, 0)

    # A local point p maps to matrix_world @ (P_local @ p); with the object at x=2 and the
    # plane at x=5, a point 1 unit along local +x sits at x=3 and must end up at x=7.
    p = Vector((1.0, 0.0, 0.0))
    assert np.allclose(list(obj.matrix_world @ Vector((-p.x, p.y, p.z))), [7.0, 0.0, 0.0])


def test_the_mirror_plane_passes_through_the_middle_of_the_reference():
    """An IFC origin is arbitrary, so the plane has to sit at what the user can see.

    The reference here spans local x 0..4 with its origin at the near corner, so the plane is
    at x = 2 in local terms, which is x = 12 in the world.
    """
    operator = _operator()
    corners = [(x, y, z) for x in (0.0, 4.0) for y in (0.0, 1.0) for z in (0.0, 3.0)]
    # get_object_bounding_box reads bound_box[0] as the minimum and bound_box[6] as the maximum
    bound_box = [(0.0, 0.0, 0.0), None, None, None, None, None, (4.0, 1.0, 3.0), None]
    reference = SimpleNamespace(matrix_world=Matrix.Translation((10.0, 0.0, 0.0)), bound_box=bound_box)
    assert list(operator.get_mirror_plane_point(reference)) == [12.0, 0.5, 1.5]
    assert corners  # the bounds above describe a real box

    obj = SimpleNamespace(matrix_world=Matrix.Translation((3.0, 0.0, 0.0)), location=None)
    operator.reflect_placement(obj, reference, (1.0, 0.0, 0.0), {}, 0)
    # the object origin sits 9 units to the left of the plane, so it lands 9 to the right
    assert np.allclose(list(obj.matrix_world.translation), [21.0, 0.0, 0.0])


def test_the_mirror_plane_ignores_an_active_object_that_is_not_selected():
    """Blender keeps an object active after deselecting it. It is not a visible mirror plane."""
    from bonsai.bim.module.model.product import MirrorElements

    target = SimpleNamespace(name="target", select_get=lambda: True)
    ghost = SimpleNamespace(name="ghost", select_get=lambda: False)
    context = SimpleNamespace(active_object=ghost, selected_objects=[target])

    seen = []

    class Stub:
        _execute = MirrorElements._execute
        resolve_selection = MirrorElements.__dict__["resolve_selection"]
        mirror_axis = "X"

        def mirror_obj(self, context, obj, mirror_ref=None, axis_index=0):
            seen.append((obj.name, mirror_ref.name if mirror_ref else None))
            return True

        def report(self, level, message):
            pass

    Stub()._execute(context)
    assert seen == [("target", None)], "a deselected active object must not become the mirror plane"


def test_get_mirror_axes_never_flips_more_than_one_axis():
    operator = _operator()
    obj = SimpleNamespace(matrix_world=Matrix.Identity(4))
    for angle in (0, 30, 45, 60, 90, 135):
        reference = SimpleNamespace(matrix_world=Matrix.Rotation(np.radians(angle), 4, "Z"))
        axes = operator.get_mirror_axes(obj, reference)
        assert sum(axes) == 1.0, f"{angle} degrees produced {axes}"


def test_get_mirror_axes_without_a_reference_uses_the_local_yz_plane():
    operator = _operator()
    obj = SimpleNamespace(matrix_world=Matrix.Identity(4))
    assert operator.get_mirror_axes(obj, None) == (1.0, 0.0, 0.0)


def test_get_mirror_axes_without_a_reference_honours_the_chosen_axis():
    operator = _operator()
    obj = SimpleNamespace(matrix_world=Matrix.Identity(4))
    assert operator.get_mirror_axes(obj, None, 1) == (0.0, 1.0, 0.0)
    assert operator.get_mirror_axes(obj, None, 2) == (0.0, 0.0, 1.0)


def test_get_mirror_axes_uses_the_chosen_axis_of_the_reference():
    """A reference turned 90 degrees about Z has its local Y pointing along world -X."""
    operator = _operator()
    obj = SimpleNamespace(matrix_world=Matrix.Identity(4))
    reference = SimpleNamespace(matrix_world=Matrix.Rotation(np.radians(90), 4, "Z"))
    assert operator.get_mirror_axes(obj, reference, 0) == (0.0, 1.0, 0.0)
    assert operator.get_mirror_axes(obj, reference, 1) == (1.0, 0.0, 0.0)
    assert operator.get_mirror_axes(obj, reference, 2) == (0.0, 0.0, 1.0)


def test_a_swept_solid_reports_that_it_cannot_be_inverted_along_z():
    """ShapeBuilder.mirror is 2D, so a Z mirror must be refused rather than half applied."""
    ifc_file, _, occurrences, _ = _mapped_type_file()
    element_type = ifc_file.by_type("IfcFurnitureType")[0]
    operator = _operator()

    with patch("bonsai.tool.Ifc.get", return_value=ifc_file):
        assert operator.find_uninvertible_items(element_type, (1.0, 0.0, 0.0)) == set()
        assert operator.find_uninvertible_items(element_type, (0.0, 1.0, 0.0)) == set()
        assert operator.find_uninvertible_items(element_type, (0.0, 0.0, 1.0)) == {"IfcExtrudedAreaSolid along Z"}


def test_find_uninvertible_items_refuses_shared_type_geometry_before_mutating():
    from bonsai.bim.module.model.product import SharedMappedGeometryError

    ifc_file, _, occurrences, solid = _mapped_type_file()
    coordinates_before = _profile_coordinates(solid)
    operator = _operator()

    with patch("bonsai.tool.Ifc.get", return_value=ifc_file):
        with pytest.raises(SharedMappedGeometryError):
            operator.find_uninvertible_items(occurrences[0], (1.0, 0.0, 0.0))

    assert _profile_coordinates(solid) == coordinates_before
