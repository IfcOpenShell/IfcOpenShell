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

import os
import bpy
import numpy as np
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
    def get_path(cls):
        return IfcStore.path

    @classmethod
    def get_schema(cls):
        if IfcStore.get_file():
            return IfcStore.get_file().schema

    @classmethod
    def is_deleted(cls, element):
        return element.id() in IfcStore.deleted_ids

    @classmethod
    def is_edited(cls, obj):
        return list(obj.scale) != [1.0, 1.0, 1.0] or obj in IfcStore.edited_objs

    @classmethod
    def is_moved(cls, obj):
        if not obj.BIMObjectProperties.location_checksum:
            return True  # Let's be conservative
        loc_check = np.frombuffer(eval(obj.BIMObjectProperties.location_checksum))
        rot_check = np.frombuffer(eval(obj.BIMObjectProperties.rotation_checksum))
        loc_real = np.array(obj.matrix_world.translation).flatten()
        rot_real = np.array(obj.matrix_world.to_3x3()).flatten()
        if np.allclose(loc_check, loc_real, atol=1e-4) and np.allclose(rot_check, rot_real, atol=1e-2):
            return False
        return True

    @classmethod
    def schema(cls):
        return IfcStore.get_schema()

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
    def delete(cls, element):
        IfcStore.delete_element(element)

    @classmethod
    def resolve_uri(cls, uri):
        return uri if not uri or os.path.isabs(uri) else os.path.join(os.path.dirname(cls.get_path()), uri)

    @classmethod
    def unlink(cls, element=None, obj=None):
        IfcStore.unlink_element(element, obj)

    class Operator:
        def execute(self, context):
            IfcStore.execute_ifc_operator(self, context)
            blenderbim.bim.handler.refresh_ui_data()
            return {"FINISHED"}
