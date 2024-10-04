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

import bpy
import bonsai.bim.helper
import bonsai.tool as tool
import bonsai.core.tool
import ifcopenshell
from typing import Any, Union


class Context(bonsai.core.tool.Context):
    @classmethod
    def set_context(cls, context: ifcopenshell.entity_instance) -> None:
        bpy.context.scene.BIMContextProperties.active_context_id = context.id()

    @classmethod
    def import_attributes(cls) -> None:
        props = bpy.context.scene.BIMContextProperties
        props.context_attributes.clear()
        context = cls.get_context()

        def callback(name: str, prop, data) -> Union[bool, None]:
            if context.is_a("IfcGeometricRepresentationSubContext"):
                if name == "Precision":
                    props.context_attributes.remove(props.context_attributes.find("Precision"))
                    return True
                elif name == "CoordinateSpaceDimension":
                    props.context_attributes.remove(props.context_attributes.find("CoordinateSpaceDimension"))
                    return True
            else:  # IfcGeometricRepresentationContext
                # Import precision as a string because Blender has problem displaying 1e-7 and smaller numbers in UI.
                if name == "Precision":
                    prop.data_type = "string"

        bonsai.bim.helper.import_attributes(context.is_a(), props.context_attributes, context.get_info(), callback)

    @classmethod
    def clear_context(cls) -> None:
        bpy.context.scene.BIMContextProperties.active_context_id = 0

    @classmethod
    def get_context(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_id(bpy.context.scene.BIMContextProperties.active_context_id)

    @classmethod
    def export_attributes(cls) -> dict[str, Any]:
        def callback(attributes, blender_attribute) -> bool:
            if blender_attribute.name == "Precision":
                attributes["Precision"] = float(blender_attribute.get_value())
                return True
            return False

        return bonsai.bim.helper.export_attributes(
            bpy.context.scene.BIMContextProperties.context_attributes, callback=callback
        )
