# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of BlenderBIM Add-on.
#
# BlenderBIM Add-on is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# BlenderBIM Add-on is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with BlenderBIM Add-on.  If not, see <http://www.gnu.org/licenses/>.

import bpy
import blenderbim.bim.helper
import blenderbim.tool as tool
import blenderbim.core.tool


class Context(blenderbim.core.tool.Context):
    @classmethod
    def set_context(cls, context):
        bpy.context.scene.BIMContextProperties.active_context_id = context.id()

    @classmethod
    def import_attributes(cls):
        props = bpy.context.scene.BIMContextProperties
        props.context_attributes.clear()
        context = cls.get_context()

        def callback(name, prop, data):
            if context.is_a("IfcGeometricRepresentationSubContext"):
                if name == "Precision":
                    props.context_attributes.remove(props.context_attributes.find("Precision"))
                    return True
                elif name == "CoordinateSpaceDimension":
                    props.context_attributes.remove(props.context_attributes.find("CoordinateSpaceDimension"))
                    return True

        blenderbim.bim.helper.import_attributes(context.is_a(), props.context_attributes, context.get_info(), callback)

    @classmethod
    def clear_context(cls):
        bpy.context.scene.BIMContextProperties.active_context_id = 0

    @classmethod
    def get_context(cls):
        return tool.Ifc.get().by_id(bpy.context.scene.BIMContextProperties.active_context_id)

    @classmethod
    def export_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMContextProperties.context_attributes)
