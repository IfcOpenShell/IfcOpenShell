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
import ifcopenshell
import ifcopenshell.util.attribute
import ifcopenshell.util.doc
import ifcopenshell.util.element
import bonsai.tool as tool
import bonsai.bim.schema


# TODO: Should this cache belong here? Dunno. Maybe.
is_expanded = {}


def refresh():
    ObjectPsetsData.is_loaded = False
    ObjectQtosData.is_loaded = False
    MaterialPsetsData.is_loaded = False
    MaterialSetPsetsData.is_loaded = False
    MaterialSetItemPsetsData.is_loaded = False
    TaskQtosData.is_loaded = False
    ResourceQtosData.is_loaded = False
    ResourcePsetsData.is_loaded = False
    GroupQtosData.is_loaded = False
    GroupPsetData.is_loaded = False
    ProfilePsetsData.is_loaded = False
    WorkSchedulePsetsData.is_loaded = False
    AddEditCustomPropertiesData.is_loaded = False


class Data:
    @classmethod
    def psetqtos(cls, element: ifcopenshell.entity_instance, psets_only: bool = False, qtos_only: bool = False):
        ifc_file = tool.Ifc.get()
        results = []
        psetqtos = ifcopenshell.util.element.get_psets(
            element, psets_only=psets_only, qtos_only=qtos_only, should_inherit=False
        )
        for name, data in sorted(psetqtos.items()):
            pset = ifc_file.by_id(data["id"])
            pset_uses = ifcopenshell.util.element.get_elements_by_pset(pset)
            has_template = bool(tool.Pset.get_pset_template(name))
            results.append(
                {
                    "id": data["id"],
                    "Name": name,
                    "is_expanded": is_expanded.get(data["id"], True),
                    "Properties": [{"Name": k, "NominalValue": v} for k, v in sorted(data.items()) if k != "id"],
                    "shared_pset_uses": len(pset_uses),
                    "has_template": has_template,
                }
            )
        return sorted(results, key=lambda v: v["Name"])

    @classmethod
    def format_pset_enum(cls, psets):
        enum_items = []
        version = tool.Ifc.get_schema()
        for pset in psets:
            doc = ifcopenshell.util.doc.get_property_set_doc(version, pset.Name) or {}
            enum_items.append((pset.Name, pset.Name, doc.get("description", "")))
        return enum_items


class ObjectPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "is_occurrence": cls.is_occurrence(),
            "psets": cls.psetqtos(tool.Ifc.get_entity(bpy.context.active_object), psets_only=True),
            "inherited_psets": cls.inherited_psets(),
            "pset_name": cls.pset_name(),
            "qto_name": cls.qto_name(),
        }
        cls.is_loaded = True

    @classmethod
    def is_occurrence(cls):
        return not tool.Ifc.get_entity(bpy.context.active_object).is_a("IfcTypeObject")

    @classmethod
    def inherited_psets(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element.is_a("IfcTypeObject"):
            return []
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            return cls.psetqtos(element_type, psets_only=True)

    @classmethod
    def pset_name(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        psets = bonsai.bim.schema.ifc.psetqto.get_applicable(
            element.is_a(), ifcopenshell.util.element.get_predefined_type(element), pset_only=True
        )
        psetnames = cls.format_pset_enum(psets)
        assigned_names = ifcopenshell.util.element.get_psets(element, psets_only=True, should_inherit=False).keys()
        return [p for p in psetnames if p[0] not in assigned_names]

    @classmethod
    def qto_name(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        qtos = bonsai.bim.schema.ifc.psetqto.get_applicable(
            element.is_a(), ifcopenshell.util.element.get_predefined_type(element), qto_only=True
        )
        return cls.format_pset_enum(qtos)


class ObjectQtosData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "is_occurrence": cls.is_occurrence(),
            "qtos": cls.psetqtos(tool.Ifc.get_entity(bpy.context.active_object), qtos_only=True),
            "inherited_qsets": cls.inherited_qsets(),
        }
        cls.is_loaded = True

    @classmethod
    def is_occurrence(cls):
        return not tool.Ifc.get_entity(bpy.context.active_object).is_a("IfcTypeObject")

    @classmethod
    def inherited_qsets(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element.is_a("IfcTypeObject"):
            return []
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            return cls.psetqtos(element_type, qtos_only=True)


class MaterialPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        ifc_definition_id = None
        props = bpy.context.scene.BIMMaterialProperties
        if props.materials and props.active_material_index < len(props.materials):
            ifc_definition_id = props.materials[props.active_material_index].ifc_definition_id

        cls.data = {
            "ifc_definition_id": ifc_definition_id,
            "psets": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id)),
            "pset_name": cls.pset_name(),
        }
        cls.is_loaded = True

    @classmethod
    def pset_name(cls):
        props = bpy.context.scene.BIMMaterialProperties
        if props.materials and props.active_material_index < len(props.materials):
            material = props.materials[props.active_material_index]
            if material.ifc_definition_id:
                material = tool.Ifc.get().by_id(material.ifc_definition_id)
                category = getattr(material, "Category", None) or None
                psets = bonsai.bim.schema.ifc.psetqto.get_applicable("IfcMaterial", category, pset_only=True)
                psetnames = cls.format_pset_enum(psets)
                assigned_names = ifcopenshell.util.element.get_psets(
                    material, psets_only=True, should_inherit=False
                ).keys()
                return [p for p in psetnames if p[0] not in assigned_names]
        return []


class MaterialSetPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        psets = {}
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element:
            material = ifcopenshell.util.element.get_material(element, should_skip_usage=True)
            if material and "Set" in material.is_a():
                psets = cls.psetqtos(material)
        cls.data = {"psets": psets}
        cls.is_loaded = True


class MaterialSetItemPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        psets = {}
        ifc_definition_id = bpy.context.active_object.BIMObjectMaterialProperties.active_material_set_item_id
        if ifc_definition_id:
            psets = cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id))
        cls.data = {"psets": psets}
        cls.is_loaded = True


class TaskQtosData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        wprops = bpy.context.scene.BIMWorkScheduleProperties
        tprops = bpy.context.scene.BIMTaskTreeProperties
        ifc_definition_id = tprops.tasks[wprops.active_task_index].ifc_definition_id
        cls.data = {"qtos": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), qtos_only=True)}
        cls.is_loaded = True


class ResourceQtosData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        rprops = bpy.context.scene.BIMResourceProperties
        rtprops = bpy.context.scene.BIMResourceTreeProperties
        ifc_definition_id = rtprops.resources[rprops.active_resource_index].ifc_definition_id
        cls.data = {"qtos": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), qtos_only=True)}
        cls.is_loaded = True


class ResourcePsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        rprops = bpy.context.scene.BIMResourceProperties
        rtprops = bpy.context.scene.BIMResourceTreeProperties
        ifc_definition_id = rtprops.resources[rprops.active_resource_index].ifc_definition_id
        cls.data = {"psets": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), psets_only=True)}
        cls.is_loaded = True


class GroupQtosData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        props = bpy.context.scene.BIMGroupProperties
        ifc_definition_id = props.groups[props.active_group_index].ifc_definition_id
        cls.data = {"qtos": cls.psetqtos(tool.Ifc.get_entity_by_id(ifc_definition_id), qtos_only=True)}
        cls.is_loaded = True


class GroupPsetData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        props = bpy.context.scene.BIMGroupProperties
        ifc_definition_id = props.groups[props.active_group_index].ifc_definition_id
        cls.data = {"psets": cls.psetqtos(tool.Ifc.get_entity_by_id(ifc_definition_id), psets_only=True)}
        cls.is_loaded = True


class ProfilePsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        active_profile = tool.Profile.get_active_profile_ui()
        if active_profile:
            ifc_definition_id = active_profile.ifc_definition_id
            psets_data = cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), psets_only=True)
        else:
            ifc_definition_id = 0
            psets_data = []

        cls.data = {
            "ifc_definition_id": ifc_definition_id,
            "psets": psets_data,
        }
        cls.is_loaded = True


class WorkSchedulePsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        ifc_definition_id = bpy.context.scene.BIMWorkScheduleProperties.active_work_schedule_id
        cls.data = {"psets": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), psets_only=True)}
        cls.is_loaded = True


class AddEditCustomPropertiesData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"primary_measure_type": cls.primary_measure_type()}
        cls.is_loaded = True

    @classmethod
    def primary_measure_type(cls):
        SIMPLE_TYPES = {"string", "integer", "float", "boolean"}
        schema = tool.Ifc.schema()
        version = tool.Ifc.get_schema()
        # Skip non-simple types as they're currently not supported (e.g. IfcBinary and lists/arrays/sets of types).
        declarations = [
            d.name()
            for d in schema.declarations()
            if hasattr(d, "declared_type") and ifcopenshell.util.attribute.get_primitive_type(d) in SIMPLE_TYPES
        ]
        return [
            (t, t, ifcopenshell.util.doc.get_type_doc(version, t).get("description", "")) for t in sorted(declarations)
        ]
