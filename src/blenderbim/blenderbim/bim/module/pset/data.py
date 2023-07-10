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
import ifcopenshell
import ifcopenshell.util.doc
import blenderbim.tool as tool
import blenderbim.bim.schema


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
    ProfilePsetsData.is_loaded = False
    WorkSchedulePsetsData.is_loaded = False
    AddEditCustomPropertiesData.is_loaded = False


class Data:
    @classmethod
    def psetqtos(cls, element, psets_only=False, qtos_only=False):
        results = []
        psetqtos = ifcopenshell.util.element.get_psets(
            element, psets_only=psets_only, qtos_only=qtos_only, should_inherit=False
        )
        for name, data in psetqtos.items():
            results.append(
                {
                    "id": data["id"],
                    "Name": name,
                    "is_expanded": is_expanded.get(data["id"], True),
                    "Properties": [{"Name": k, "NominalValue": v} for k, v in data.items() if k != "id"],
                }
            )
        return sorted(results, key=lambda v: v["Name"])


class ObjectPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "psets": cls.psetqtos(tool.Ifc.get_entity(bpy.context.active_object), psets_only=True),
            "inherited_psets": cls.inherited_psets(),
            "pset_name": cls.pset_name(),
            "qto_name": cls.qto_name(),
        }
        cls.is_loaded = True

    @classmethod
    def inherited_psets(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        if element.is_a("IfcTypeObject"):
            return
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type:
            return cls.psetqtos(element_type)

    @classmethod
    def pset_name(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        psets = blenderbim.bim.schema.ifc.psetqto.get_applicable(element.is_a(), pset_only=True)
        psetnames = cls.format_pset_enum(psets)
        assigned_names = ifcopenshell.util.element.get_psets(element, psets_only=True).keys()
        return [p for p in psetnames if p[0] not in assigned_names]

    @classmethod
    def qto_name(cls):
        obj = bpy.context.active_object
        element = tool.Ifc.get_entity(obj)
        if not element:
            return []
        qtos = blenderbim.bim.schema.ifc.psetqto.get_applicable(element.is_a(), qto_only=True)
        return cls.format_pset_enum(qtos)

    @classmethod
    def format_pset_enum(cls, psets):
        enum_items = []
        version = tool.Ifc.get_schema()
        for pset in psets:
            doc = ifcopenshell.util.doc.get_property_set_doc(version, pset.Name) or {}
            enum_items.append((pset.Name, pset.Name, doc.get("description", "")))
        return enum_items


class ObjectQtosData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"qtos": cls.psetqtos(tool.Ifc.get_entity(bpy.context.active_object), qtos_only=True)}
        cls.is_loaded = True


class MaterialPsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "ifc_definition_id": bpy.context.active_object.active_material.BIMObjectProperties.ifc_definition_id,
            "psets": cls.psetqtos(tool.Ifc.get_entity(bpy.context.active_object.active_material)),
        }
        cls.is_loaded = True


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


class ProfilePsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        pprops = bpy.context.scene.BIMProfileProperties
        ifc_definition_id = pprops.profiles[pprops.active_profile_index].ifc_definition_id
        cls.data = {"psets": cls.psetqtos(tool.Ifc.get().by_id(ifc_definition_id), psets_only=True)}
        cls.is_loaded = True


class WorkSchedulePsetsData(Data):
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        props = bpy.context.scene.WorkSchedulePsetProperties
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
        schema = tool.Ifc.schema()
        version = tool.Ifc.get_schema()
        return [
            (t, t, ifcopenshell.util.doc.get_type_doc(version, t).get("description", ""))
            for t in sorted([d.name() for d in schema.declarations() if hasattr(d, "declared_type")])
        ]
