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

"""Regression test for #9006: the Door Tool's "Add" button crashed when the
selected relating type reached ``bim.draw_polyline_profile`` without a real
``IfcMaterialProfileSet``.

``DumbProfileGenerator.generate()`` already documents ``None`` as a valid
return in its own type annotation, and hits it whenever the relating type
has no ``IfcMaterialProfileSet`` (e.g. a plain ``IfcDoorType``, or a type
carrying an ``IfcMaterialProfileSetUsage`` instead of the raw Set -
``get_usage_type()`` treats both as ``"PROFILE"``, but only the raw Set is
drawable). ``create_profiles_from_polyline`` used to unpack that ``None``
unconditionally, raising ``TypeError: cannot unpack non-iterable NoneType
object`` - exactly the crash reported in #9006.

The fix has two layers, both covered here:
1. ``tool.Model.get_material_profile_set`` is the single source of truth for
   "can DumbProfileGenerator actually draw this", now shared by both the
   generator and the routing decision in ``hotkey_S_A``
   (``bonsai/bim/module/model/workspace.py``) that picks
   ``bim.draw_polyline_profile`` vs. ``bim.draw_occurrence``.
2. ``create_profiles_from_polyline`` no longer unpacks a ``None`` result -
   it reports a warning and cancels instead of crashing, so any other path
   that reaches this operator degrades gracefully too."""

from unittest.mock import Mock, patch

import ifcopenshell
import pytest

pytestmark = pytest.mark.model


def _make_file():
    return ifcopenshell.file(schema="IFC4")


def _make_door_type(ifc_file):
    return ifc_file.create_entity(
        "IfcDoorType",
        GlobalId=ifcopenshell.guid.new(),
        PredefinedType="DOOR",
    )


def _assign_profile_set_usage(ifc_file, element):
    """Mirrors what a real IfcMaterialProfileSetUsage association looks
    like: get_usage_type() reports "PROFILE" for it, but it is not a
    genuine IfcMaterialProfileSet."""
    profile = ifc_file.create_entity(
        "IfcRectangleProfileDef", ProfileName="Test Profile", ProfileType="AREA", XDim=0.1, YDim=0.1
    )
    material = ifc_file.create_entity("IfcMaterial", Name="Test Material")
    material_profile = ifc_file.create_entity("IfcMaterialProfile", Material=material, Profile=profile)
    profile_set = ifc_file.create_entity("IfcMaterialProfileSet", MaterialProfiles=[material_profile])
    usage = ifc_file.create_entity("IfcMaterialProfileSetUsage", ForProfileSet=profile_set, CardinalPoint=5)
    ifc_file.create_entity(
        "IfcRelAssociatesMaterial",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[element],
        RelatingMaterial=usage,
    )
    return profile_set


def _assign_profile_set(ifc_file, element):
    profile = ifc_file.create_entity(
        "IfcRectangleProfileDef", ProfileName="Test Profile", ProfileType="AREA", XDim=0.1, YDim=0.1
    )
    material = ifc_file.create_entity("IfcMaterial", Name="Test Material")
    material_profile = ifc_file.create_entity("IfcMaterialProfile", Material=material, Profile=profile)
    profile_set = ifc_file.create_entity("IfcMaterialProfileSet", MaterialProfiles=[material_profile])
    ifc_file.create_entity(
        "IfcRelAssociatesMaterial",
        GlobalId=ifcopenshell.guid.new(),
        RelatedObjects=[element],
        RelatingMaterial=profile_set,
    )
    return profile_set


def test_get_material_profile_set_rejects_type_with_no_material():
    from bonsai import tool

    ifc_file = _make_file()
    door_type = _make_door_type(ifc_file)

    assert tool.Model.get_material_profile_set(door_type) is None


def test_get_material_profile_set_rejects_profile_set_usage():
    """get_usage_type() reports "PROFILE" for an IfcMaterialProfileSetUsage,
    but DumbProfileGenerator can't draw from a usage - get_material_profile_set
    must reject it too, or the two functions disagree again."""
    from bonsai import tool

    ifc_file = _make_file()
    door_type = _make_door_type(ifc_file)
    _assign_profile_set_usage(ifc_file, door_type)

    assert tool.Model.get_usage_type(door_type) == "PROFILE"
    assert tool.Model.get_material_profile_set(door_type) is None


def test_get_material_profile_set_accepts_genuine_profile_set():
    from bonsai import tool

    ifc_file = _make_file()
    door_type = _make_door_type(ifc_file)
    profile_set = _assign_profile_set(ifc_file, door_type)

    assert tool.Model.get_material_profile_set(door_type) == profile_set


def test_generate_polyline_returns_none_instead_of_raising_for_ineligible_type():
    """The exact call at the #9006 crash site: DumbProfileGenerator(relating_type)
    .generate("POLYLINE") must return None (not raise) when relating_type has
    no drawable profile set, matching its own documented return type."""
    from bonsai import tool
    from bonsai.bim.module.model.profile import DumbProfileGenerator

    ifc_file = _make_file()
    door_type = _make_door_type(ifc_file)
    _assign_profile_set_usage(ifc_file, door_type)

    with patch.object(tool.Ifc, "get", return_value=ifc_file):
        result = DumbProfileGenerator(door_type).generate("POLYLINE")

    assert result is None


def test_create_profiles_from_polyline_reports_and_cancels_instead_of_crashing():
    """Regression test for the reported TypeError: unbound-call
    create_profiles_from_polyline with a duck-typed operator ``self`` so the
    exact #9006 crash site is exercised without a full modal operator."""
    from bonsai.bim.module.model.profile import DrawPolylineProfile

    ifc_file = _make_file()
    door_type = _make_door_type(ifc_file)
    _assign_profile_set_usage(ifc_file, door_type)

    fake_self = Mock()
    fake_self.relating_type = door_type

    with patch("bonsai.bim.module.model.profile.tool.Ifc.get", return_value=ifc_file):
        result = DrawPolylineProfile.create_profiles_from_polyline(fake_self, context=Mock())

    assert result == {"CANCELLED"}
    fake_self.report.assert_called_once()
    assert fake_self.report.call_args.args[0] == {"WARNING"}
