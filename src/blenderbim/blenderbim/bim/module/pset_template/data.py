# BlenderBIM Add-on - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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
import ifcopenshell
import blenderbim.tool as tool
from blenderbim.bim.ifc import IfcStore


def refresh():
    PsetTemplatesData.is_loaded = False


class PsetTemplatesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["primary_measure_type"] = cls.primary_measure_type()
        cls.data["pset_template_files"] = cls.pset_template_files()
        cls.data["pset_templates"] = cls.pset_templates()
        cls.data["pset_template"] = cls.pset_template()
        cls.data["prop_templates"] = cls.prop_templates()

    @classmethod
    def primary_measure_type(cls):
        schema = tool.Ifc.schema()
        return [(t, t, "") for t in sorted([d.name() for d in schema.declarations() if hasattr(d, "declared_type")])]

    @classmethod
    def pset_template_files(cls):
        files = os.listdir(os.path.join(bpy.context.scene.BIMProperties.data_dir, "pset"))
        return [(f.replace(".ifc", ""), f.replace(".ifc", ""), "") for f in files]

    @classmethod
    def pset_templates(cls):
        if not IfcStore.pset_template_file:
            IfcStore.pset_template_path = os.path.join(
                bpy.context.scene.BIMProperties.data_dir,
                "pset",
                bpy.context.scene.BIMPsetTemplateProperties.pset_template_files + ".ifc",
            )
            IfcStore.pset_template_file = ifcopenshell.open(IfcStore.pset_template_path)
        return [(str(t.id()), t.Name, "") for t in IfcStore.pset_template_file.by_type("IfcPropertySetTemplate")]

    @classmethod
    def pset_template(cls):
        props = bpy.context.scene.BIMPsetTemplateProperties
        template_id = props.pset_templates
        if not template_id:
            return {}
        info = IfcStore.pset_template_file.by_id(int(template_id)).get_info()
        del info["id"]
        del info["type"]
        del info["OwnerHistory"]
        del info["HasPropertyTemplates"]
        return info

    @classmethod
    def prop_templates(cls):
        props = bpy.context.scene.BIMPsetTemplateProperties
        template_id = props.pset_templates
        if not template_id:
            return []
        return [e.get_info() for e in IfcStore.pset_template_file.by_id(int(template_id)).HasPropertyTemplates or []]
