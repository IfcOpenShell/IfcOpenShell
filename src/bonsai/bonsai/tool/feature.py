# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
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

from __future__ import annotations
import bpy
import bonsai.core.tool
import bonsai.tool as tool
import bonsai.bim.helper
import bonsai.core.geometry
import ifcopenshell
import ifcopenshell.util.representation
from typing import Iterable, TYPE_CHECKING

if TYPE_CHECKING:
    from bonsai.bim.module.void.prop import BIMBooleanProperties


class Feature(bonsai.core.tool.Feature):
    # TODO: consolidate module/model/opening and module/void into new module/feature

    @classmethod
    def get_boolean_props(cls) -> BIMBooleanProperties:
        return bpy.context.scene.BIMBooleanProperties

    @classmethod
    def add_feature(cls, featured_obj: bpy.types.Object, feature_objs: Iterable[bpy.types.Object]) -> None:
        featured_element = tool.Ifc.get_entity(featured_obj)

        has_visible_openings = False
        for opening in [r.RelatedOpeningElement for r in featured_element.HasOpenings]:
            if tool.Ifc.get_object(opening):
                has_visible_openings = True
                break

        for feature_obj in feature_objs:
            feature_element = tool.Ifc.get_entity(feature_obj)

            # Sync placement before feature.add_feature.
            if tool.Ifc.is_moved(featured_obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=featured_obj)

            element_had_openings = tool.Geometry.has_openings(featured_element)
            body_context = ifcopenshell.util.representation.get_context(tool.Ifc.get(), "Model", "Body")
            ifcopenshell.api.run(
                "feature.add_feature", tool.Ifc.get(), feature=feature_element, element=featured_element
            )

            if tool.Ifc.is_moved(feature_obj):
                bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=feature_obj)

        voided_objs = [featured_obj]
        for subelement in tool.Aggregate.get_parts_recursively(featured_element):
            if subobj := tool.Ifc.get_object(subelement):
                voided_objs.append(subobj)

        for voided_obj in voided_objs:
            if voided_obj.data:
                if tool.Ifc.is_edited(voided_obj):
                    voided_element_ = tool.Ifc.get_entity(voided_obj)
                    if element_had_openings or (voided_element_ != featured_element and voided_element_.HasOpenings):
                        voided_obj.scale = (1.0, 1.0, 1.0)
                        tool.Ifc.finish_edit(voided_obj)
                    else:
                        bpy.ops.bim.update_representation(obj=voided_obj.name)

                if tool.Ifc.is_moved(voided_obj):
                    bonsai.core.geometry.edit_object_placement(tool.Ifc, tool.Geometry, tool.Surveyor, obj=voided_obj)

                tool.Geometry.reload_representation(voided_obj)
            tool.Geometry.lock_scale(voided_obj)
