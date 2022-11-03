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
import ifcopenshell.util.schema
import blenderbim.tool as tool


def refresh():
    MaterialsData.is_loaded = False
    ObjectMaterialData.is_loaded = False


class MaterialsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {
            "total_materials": cls.total_materials(),
            "material_types": cls.material_types(),
            "profiles": cls.profiles(),
        }
        cls.is_loaded = True

    @classmethod
    def total_materials(cls):
        if tool.Ifc.get_schema() == "IFC2X3":
            return (
                len(tool.Ifc.get().by_type("IfcMaterial"))
                + len(tool.Ifc.get().by_type("IfcMaterialLayerSet"))
                + len(tool.Ifc.get().by_type("IfcMaterialList"))
            )
        return (
            len(tool.Ifc.get().by_type("IfcMaterial"))
            + len(tool.Ifc.get().by_type("IfcMaterialConstituentSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialLayerSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialProfileSet"))
            + len(tool.Ifc.get().by_type("IfcMaterialList"))
        )

    @classmethod
    def material_types(cls):
        material_types = [
            "IfcMaterial",
            "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet",
            "IfcMaterialProfileSet",
            "IfcMaterialList",
        ]
        version = tool.Ifc.get_schema()
        if version == "IFC2X3":
            material_types = ["IfcMaterial", "IfcMaterialLayerSet", "IfcMaterialList"]
        return [(m, m, ifcopenshell.util.doc.get_entity_doc(version, m).get("description", "")) for m in material_types]

    @classmethod
    def profiles(cls):
        return [(str(p.id()), p.ProfileName or "Unnamed", "") for p in tool.Ifc.get().by_type("IfcProfileDef")]


class ObjectMaterialData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data["material_class"] = cls.material_class()
        cls.data["material_id"] = cls.material_id()
        cls.data["material_name"] = cls.material_name()
        cls.data["set"] = cls.set()
        cls.data["set_usage"] = cls.set_usage()
        cls.data["set_items"] = cls.set_items()
        cls.data["set_item_name"] = cls.set_item_name()
        cls.data["total_thickness"] = cls.total_thickness()
        cls.data["materials"] = cls.materials()
        cls.data["type_material"] = cls.type_material()
        cls.is_loaded = True

    @classmethod
    def material_class(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        cls.material = ifcopenshell.util.element.get_material(element)
        if cls.material:
            return cls.material.is_a()

    @classmethod
    def material_id(cls):
        if cls.material:
            return cls.material.id()
        return 0

    @classmethod
    def set(cls):
        mset = None
        if cls.material:
            mset = cls.material
            if cls.material.is_a("IfcMaterialLayerSetUsage"):
                mset = cls.material.ForLayerSet
            elif cls.material.is_a("IfcMaterialProfileSetUsage"):
                mset = cls.material.ForProfileSet
            return {
                "id": mset.id(),
                "name": getattr(mset, "LayerSetName", getattr(mset, "Name", None)) or "Unnamed",
                "description": getattr(mset, "Description", None),
            }

    @classmethod
    def set_usage(cls):
        # TODO: complain to buildingSMART
        cardinal_point_map = {
            1: "bottom left",
            2: "bottom centre",
            3: "bottom right",
            4: "mid-depth left",
            5: "mid-depth centre",
            6: "mid-depth right",
            7: "top left",
            8: "top centre",
            9: "top right",
            10: "geometric centroid",
            11: "bottom in line with the geometric centroid",
            12: "left in line with the geometric centroid",
            13: "right in line with the geometric centroid",
            14: "top in line with the geometric centroid",
            15: "shear centre",
            16: "bottom in line with the shear centre",
            17: "left in line with the shear centre",
            18: "right in line with the shear centre",
            19: "top in line with the shear centre",
        }
        results = {}
        if cls.material:
            if cls.material.is_a("IfcMaterialProfileSetUsage"):
                if cls.material.CardinalPoint:
                    results["cardinal_point"] = cardinal_point_map[cls.material.CardinalPoint]
        return results

    @classmethod
    def set_items(cls):
        results = []
        if cls.material:
            items = []
            if cls.material.is_a("IfcMaterialLayerSetUsage"):
                items = cls.material.ForLayerSet.MaterialLayers
            elif cls.material.is_a("IfcMaterialProfileSetUsage"):
                items = cls.material.ForProfileSet.MaterialProfiles
            elif cls.material.is_a("IfcMaterialLayerSet"):
                items = cls.material.MaterialLayers
            elif cls.material.is_a("IfcMaterialProfileSet"):
                items = cls.material.MaterialProfiles
            elif cls.material.is_a("IfcMaterialConstituentSet"):
                items = cls.material.MaterialConstituents

            icon = "LAYER_ACTIVE"
            if "Layer" in cls.material.is_a():
                icon = "ALIGN_CENTER"
            elif "Profile" in cls.material.is_a():
                icon = "ITALIC"
            elif "Constituent" in cls.material.is_a():
                icon = "POINTCLOUD_DATA"

            for item in items or []:
                data = {"id": item.id(), "name": item.Name or "Unnamed", "icon": icon}
                if item.is_a("IfcMaterialProfile") and not item.Name:
                    data["name"] = item.Profile.ProfileName or "Unnamed"
                if item.is_a("IfcMaterialLayer"):
                    data["name"] += f" ({item.LayerThickness})"
                if not item.is_a("IfcMaterialList"):
                    data["material"] = item.Material.Name or "Unnamed"
                results.append(data)
        return results

    @classmethod
    def total_thickness(cls):
        if cls.material:
            layers = []
            if cls.material.is_a("IfcMaterialLayerSetUsage"):
                layers = cls.material.ForLayerSet.MaterialLayers
            elif cls.material.is_a("IfcMaterialLayerSet"):
                layers = cls.material.MaterialLayers
            return sum([l.LayerThickness for l in layers or []])

    @classmethod
    def set_item_name(cls):
        results = []
        if cls.material:
            if "Constituent" in cls.material.is_a():
                return "constituent"
            elif "Layer" in cls.material.is_a():
                return "layer"
            elif "Profile" in cls.material.is_a():
                return "profile"
            elif "List" in cls.material.is_a():
                return "list_item"

    @classmethod
    def material_name(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        material = ifcopenshell.util.element.get_material(element)
        if material:
            return getattr(material, "Name", None) or "Unnamed"

    @classmethod
    def materials(cls):
        return sorted(
            [(str(m.id()), m.Name or "Unnamed", "") for m in tool.Ifc.get().by_type("IfcMaterial")], key=lambda x: x[1]
        )

    @classmethod
    def type_material(cls):
        element = tool.Ifc.get_entity(bpy.context.active_object)
        element_type = ifcopenshell.util.element.get_type(element)
        if element_type and element_type != element:
            material = ifcopenshell.util.element.get_material(element_type)
            if not material:
                return
            if material.is_a() in ("IfcMaterialLayerSetUsage", "IfcMaterialLayerSet"):
                name_attr = "LayerSetName"
            else:
                name_attr = "Name"
            return getattr(material, name_attr, "Unnamed") or "Unnamed"
