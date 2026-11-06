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

import bpy
import ifcopenshell.api.material
import ifcopenshell.api.root
import ifcopenshell.api.style
import ifcopenshell.util.representation

import bonsai.tool as tool
from test.bim.bootstrap import NewFile


class TestMultiMaterialProfileOccurrence(NewFile):
    def create_beam_type(self, profiles, composite_profile=None):
        ifc = tool.Ifc.get()
        context = ifcopenshell.util.representation.get_context(ifc, "Model", "Body", "MODEL_VIEW")
        beam_type = ifcopenshell.api.root.create_entity(ifc, ifc_class="IfcBeamType", name="Beam")
        profile_set = ifcopenshell.api.material.add_material_set(ifc, name="Beam", set_type="IfcMaterialProfileSet")
        styles = {}
        for name, x_dim in profiles.items():
            material = ifcopenshell.api.material.add_material(ifc, name=name)
            style = ifcopenshell.api.style.add_style(ifc, name=name)
            ifcopenshell.api.style.add_surface_style(
                ifc,
                style=style,
                ifc_class="IfcSurfaceStyleShading",
                attributes={"SurfaceColour": {"Name": name, "Red": 1.0, "Green": 0.0, "Blue": 0.0}},
            )
            ifcopenshell.api.style.assign_material_style(ifc, material=material, style=style, context=context)
            profile = ifc.create_entity("IfcRectangleProfileDef", ProfileType="AREA", XDim=x_dim, YDim=0.2)
            material_profile = ifcopenshell.api.material.add_profile(
                ifc, profile_set=profile_set, material=material, profile=profile
            )
            material_profile.Name = name
            styles[name] = style
        if composite_profile:
            profile_set.CompositeProfile = ifc.create_entity(
                "IfcRectangleProfileDef", ProfileType="AREA", XDim=composite_profile, YDim=0.2
            )
        ifcopenshell.api.material.assign_material(
            ifc, products=[beam_type], type="IfcMaterialProfileSet", material=profile_set
        )
        return beam_type, styles

    def add_occurrence(self, beam_type):
        bpy.ops.bim.add_occurrence(relating_type_id=beam_type.id())
        element = tool.Ifc.get_entity(bpy.context.active_object)
        body = ifcopenshell.util.representation.get_representation(element, "Model", "Body", "MODEL_VIEW")
        return element, body

    def test_each_material_profile_becomes_an_item_with_a_shape_aspect_and_style(self):
        bpy.ops.bim.create_project()
        beam_type, styles = self.create_beam_type({"Steel": 0.1, "Timber": 0.3})
        element, body = self.add_occurrence(beam_type)

        assert len(body.Items) == 2
        aspects = {aspect.Name: aspect for aspect in element.Representation.HasShapeAspects}
        assert set(aspects) == {"Steel", "Timber"}
        for name, aspect in aspects.items():
            (item,) = aspect.ShapeRepresentations[0].Items
            assert tool.Style.get_representation_item_style(item) == styles[name]

    def test_composite_profile_stays_a_single_item(self):
        bpy.ops.bim.create_project()
        beam_type, _ = self.create_beam_type({"Steel": 0.1, "Timber": 0.3}, composite_profile=0.4)
        element, body = self.add_occurrence(beam_type)

        assert len(body.Items) == 1
        assert not element.Representation.HasShapeAspects

    def test_single_material_profile_stays_a_single_item(self):
        bpy.ops.bim.create_project()
        beam_type, _ = self.create_beam_type({"Steel": 0.1})
        element, body = self.add_occurrence(beam_type)

        assert len(body.Items) == 1
        assert not element.Representation.HasShapeAspects
