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
import pathlib
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.doc
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
        cls.data["pset_template_files"] = cls.pset_template_files()

        # after pset_template_files
        cls.data["pset_templates"] = cls.pset_templates()

        # after pset_template_files because it loads IfcStore.pset_template_file
        cls.data["primary_measure_type"] = cls.primary_measure_type()
        cls.data["property_template_type"] = cls.property_template_type()
        cls.data["pset_template"] = cls.pset_template()
        cls.data["prop_templates"] = cls.prop_templates()

    @classmethod
    def primary_measure_type(cls):
        ifc_file = IfcStore.pset_template_file
        if not ifc_file:
            return []
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
        version = ifc_file.schema
        return [
            (t, t, ifcopenshell.util.doc.get_type_doc(version, t).get("description", ""))
            for t in sorted([d.name() for d in schema.declarations() if hasattr(d, "declared_type")])
        ]

    @classmethod
    def property_template_type(cls):
        ifc_file = IfcStore.pset_template_file
        if not ifc_file:
            return []
        schema = ifcopenshell.ifcopenshell_wrapper.schema_by_name(ifc_file.schema)
        attribute = schema.declaration_by_name("IfcSimplePropertyTemplate").attributes()[0]
        return [(i, i, "") for i in ifcopenshell.util.attribute.get_enum_items(attribute)]

    @classmethod
    def pset_template_files(cls):
        results = []
        pset_dir = os.path.join(bpy.context.scene.BIMProperties.data_dir, "pset")
        files = os.listdir(pset_dir)
        for f in files:
            results.append((os.path.join(pset_dir, f), os.path.splitext(os.path.basename(f))[0], "Global Pset Template"))

        pset_dir = tool.Ifc.resolve_uri(bpy.context.scene.BIMProperties.pset_dir)
        if os.path.isdir(pset_dir):
            for path in pathlib.Path(pset_dir).glob("*.ifc"):
                results.append((str(path), os.path.splitext(os.path.basename(str(path)))[0], "Project Pset Template"))

        return sorted(results, key=lambda x: x[1])

    @classmethod
    def pset_templates(cls):
        if not IfcStore.pset_template_file:
            IfcStore.pset_template_path = bpy.context.scene.BIMPsetTemplateProperties.pset_template_files
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
