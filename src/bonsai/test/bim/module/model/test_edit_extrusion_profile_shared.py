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

"""Regression test for https://github.com/IfcOpenShell/IfcOpenShell/issues/7614.

Editing an extrusion's profile in the scene (Tab into item/profile edit mode,
edit the mesh, Tab out -> ``bim.edit_extrusion_profile``) replaces the shared
``IfcProfileDef`` for every element that references it (that part already
worked: ``replace_attribute`` runs across every inverse of the old profile).
The bug was that only the actively-edited object's Blender mesh was
refreshed (``switch_representation``); sibling elements sharing the same
profile kept their stale mesh in the current session, even though their IFC
data was already correct (matching the reporter's observation that a save +
reopen fixed it, since reimporting reads the correct shared IFC data fresh).

The fix captures the sibling elements via
``ifcopenshell.util.element.get_elements_by_profile`` *before* the old
profile is replaced/removed, then reloads their Blender representations too
via ``tool.Geometry.reload_representation`` -- the same reload machinery
other profile edits already use, per the issue's scoping comment."""

from unittest.mock import Mock, patch

import pytest

pytestmark = pytest.mark.model


def _make_context(element, obj, existing_x_angle=0):
    """Minimal context/element/obj rig shared by all cases below.

    Patches every collaborator ``EditExtrusionProfile._execute`` touches
    before reaching the profile-replacement step, so the test can focus on
    the reload dispatch that runs right after it.
    """
    context = Mock()
    context.active_object = obj

    body = Mock(name="body_representation")
    extrusion = Mock(name="extrusion")
    extrusion.Position = None  # skip the position/rotation matrix math branch
    old_profile = Mock(name="old_profile")
    extrusion.SweptArea = old_profile
    new_profile = Mock(name="new_profile")

    return context, body, extrusion, old_profile, new_profile


def _run(context, body, extrusion, old_profile, new_profile, element, obj, ifc_file, sharing_elements):
    from bonsai.bim.module.model.slab import EditExtrusionProfile

    op = Mock()

    with patch("bonsai.bim.module.model.slab.ProfileDecorator"), patch(
        "bonsai.bim.module.model.slab.bpy.ops.object.mode_set"
    ), patch("bonsai.bim.module.model.slab.ifcopenshell.util.unit.calculate_unit_scale", return_value=1.0), patch(
        "bonsai.bim.module.model.slab.tool.Ifc.get_entity", return_value=element
    ), patch(
        "bonsai.bim.module.model.slab.tool.Ifc.get", return_value=ifc_file
    ), patch(
        "bonsai.bim.module.model.slab.tool.Ifc.get_object",
        side_effect=lambda e: {element: obj, **sharing_elements}.get(e),
    ), patch(
        "bonsai.bim.module.model.slab.ifcopenshell.util.representation.get_representation", return_value=body
    ), patch(
        "bonsai.bim.module.model.slab.ifcopenshell.util.representation.resolve_representation", return_value=body
    ), patch(
        "bonsai.bim.module.model.slab.tool.Model.get_extrusion", return_value=extrusion
    ), patch(
        "bonsai.bim.module.model.slab.tool.Model.get_existing_x_angle", return_value=0
    ), patch(
        "bonsai.bim.module.model.slab.tool.Model.get_material_layer_parameters", return_value={"offset": 0}
    ), patch(
        "bonsai.bim.module.model.slab.tool.Model.export_profile", return_value=new_profile
    ), patch(
        "bonsai.bim.module.model.slab.ifcopenshell.util.element.get_elements_by_profile",
        return_value=set(sharing_elements) | {element},
    ) as get_elements_by_profile, patch(
        "bonsai.bim.module.model.slab.ifcopenshell.util.element.replace_attribute"
    ), patch(
        "bonsai.bim.module.model.slab.ifcopenshell.util.element.remove_deep2"
    ), patch(
        "bonsai.bim.module.model.slab.bonsai.core.geometry.switch_representation"
    ) as switch_representation, patch(
        "bonsai.bim.module.model.slab.tool.Geometry.reload_representation"
    ) as reload_representation:
        element.is_a = Mock(return_value="IfcBuildingElementPart")
        EditExtrusionProfile._execute(op, context)

    return get_elements_by_profile, switch_representation, reload_representation


def test_edit_extrusion_profile_reloads_other_elements_sharing_profile():
    """Three elements share one profile. Editing one must reload the other
    two in the current session (this is the exact #7614 scenario)."""
    element = Mock(name="edited_element")
    obj = Mock(name="edited_obj")
    context, body, extrusion, old_profile, new_profile = _make_context(element, obj)

    sibling_a = Mock(name="sibling_a")
    sibling_b = Mock(name="sibling_b")
    obj_a = Mock(name="obj_a")
    obj_b = Mock(name="obj_b")
    ifc_file = Mock()
    ifc_file.get_inverse.return_value = []

    get_elements_by_profile, switch_representation, reload_representation = _run(
        context,
        body,
        extrusion,
        old_profile,
        new_profile,
        element,
        obj,
        ifc_file,
        {sibling_a: obj_a, sibling_b: obj_b},
    )

    # Sibling discovery must happen against the OLD profile, before it is
    # replaced/removed.
    get_elements_by_profile.assert_called_once_with(old_profile)

    # The edited object always gets switch_representation for itself.
    switch_representation.assert_called_once()
    assert switch_representation.call_args.kwargs["obj"] is obj

    # The two siblings (and only the siblings, not the edited obj again)
    # get reloaded.
    reload_representation.assert_called_once()
    (reloaded_objs,), _ = reload_representation.call_args
    assert set(reloaded_objs) == {obj_a, obj_b}


def test_edit_extrusion_profile_skips_reload_when_profile_not_shared():
    """A profile used by only one element must not trigger any reload of
    other objects (no false positives / unnecessary work)."""
    element = Mock(name="edited_element")
    obj = Mock(name="edited_obj")
    context, body, extrusion, old_profile, new_profile = _make_context(element, obj)
    ifc_file = Mock()
    ifc_file.get_inverse.return_value = []

    get_elements_by_profile, switch_representation, reload_representation = _run(
        context, body, extrusion, old_profile, new_profile, element, obj, ifc_file, {}
    )

    switch_representation.assert_called_once()
    reload_representation.assert_not_called()


def test_edit_extrusion_profile_ignores_sharing_elements_without_loaded_objects():
    """A sharing element that isn't loaded as a Blender object in this
    session (``tool.Ifc.get_object`` returns None) must be filtered out
    rather than crashing or reloading a None."""
    element = Mock(name="edited_element")
    obj = Mock(name="edited_obj")
    context, body, extrusion, old_profile, new_profile = _make_context(element, obj)

    unloaded_sibling = Mock(name="unloaded_sibling")
    ifc_file = Mock()
    ifc_file.get_inverse.return_value = []

    get_elements_by_profile, switch_representation, reload_representation = _run(
        context, body, extrusion, old_profile, new_profile, element, obj, ifc_file, {unloaded_sibling: None}
    )

    reload_representation.assert_not_called()
