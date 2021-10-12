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
import ifcopenshell.api
import blenderbim.core.tool
from blenderbim.bim.ifc import IfcStore


class Ifc(blenderbim.core.tool.Ifc):
    @classmethod
    def run(cls, command, **kwargs):
        return ifcopenshell.api.run(command, IfcStore.get_file(), **kwargs)

    @classmethod
    def set(cls, ifc):
        IfcStore.file = ifc

    @classmethod
    def get(cls):
        return IfcStore.get_file()

    @classmethod
    def get_schema(cls):
        if IfcStore.get_file():
            return IfcStore.get_file().schema

    @classmethod
    def get_entity(cls, obj):
        ifc = IfcStore.get_file()
        props = getattr(obj, "BIMObjectProperties", None)
        if ifc and props and props.ifc_definition_id:
            try:
                return IfcStore.get_file().by_id(props.ifc_definition_id)
            except:
                pass

    @classmethod
    def get_object(cls, element):
        return IfcStore.get_element(element.id())

    @classmethod
    def link(cls, element, obj):
        IfcStore.link_element(element, obj)

    @classmethod
    def unlink(cls, element=None, obj=None):
        IfcStore.unlink_element(element, obj)
