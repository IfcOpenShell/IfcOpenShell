# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2022 Dion Moult <dion@thinkmoult.com>
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

import os
import bpy
import ifcopenshell
import ifcopenshell.util.element
import ifcopenshell.util.doc
import ifcopenshell.util.schema
import bonsai.tool as tool
from bonsai.bim.module.drawing.helper import format_distance
from typing import Any, Union


def refresh():
    MaterialsData.is_loaded = False
    ObjectMaterialData.is_loaded = False


class MaterialsData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.is_loaded = True
        cls.data["material_types"] = cls.material_types()
        cls.data["total_materials"] = cls.total_materials()
        cls.data["profiles"] = cls.profiles()
        cls.data["styles"] = cls.styles()
        cls.data["contexts"] = cls.contexts()
        cls.data["material_styles_data"] = cls.material_styles_data()

    @classmethod
    def total_materials(cls):
        return len(tool.Ifc.get().by_type(bpy.context.scene.BIMMaterialProperties.material_type))

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
        return [
            (str(p.id()), p.ProfileName or "Unnamed", "")
            for p in tool.Ifc.get().by_type("IfcProfileDef")
            if p.ProfileName
        ]

    @classmethod
    def contexts(cls):
        results = []
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append((str(element.id()), element.ContextType or "Unnamed", ""))
        for element in tool.Ifc.get().by_type("IfcGeometricRepresentationSubContext", include_subtypes=False):
            results.append(
                (
                    str(element.id()),
                    "{}/{}/{}".format(
                        element.ContextType or "Unnamed",
                        element.ContextIdentifier or "Unnamed",
                        element.TargetView or "Unnamed",
                    ),
                    "",
                )
            )
        return results

    @classmethod
    def styles(cls) -> list[tuple[str, str, str]]:
        return [
            (str(s.id()), style_name or "Unnamed", "")
            for s in tool.Ifc.get().by_type("IfcPresentationStyle")
            if (style_name := s.Name)
        ]

    @classmethod
    def material_styles_data(cls) -> dict[int, list[dict[str, Any]]]:
        props = bpy.context.scene.BIMMaterialProperties
        material_styles_data: dict[int, list[dict[str, Any]]] = {}

        for material_item in props.materials:
            if not (material_id := material_item.ifc_definition_id):  # Category.
                continue

            material = tool.Ifc.get_entity_by_id(material_id)
            # NOTE: it's possible that data will be refreshed during material removal
            # (when it will try to fetch active material type and will reach for material_types)
            # and props.materials[i].ifc_definition_id will contain already removed id
            if not material or not material.is_a("IfcMaterial"):
                results = []
            else:
                results = cls.get_styles_data(material)
            material_styles_data[material_id] = results
        return material_styles_data

    @classmethod
    def get_styles_data(cls, material: ifcopenshell.entity_instance) -> list[dict[str, Any]]:
        results: list[dict[str, Any]] = []

        for definition in material.HasRepresentation:
            for representation in definition.Representations:
                if not representation.is_a("IfcStyledRepresentation"):
                    continue
                context = representation.ContextOfItems
                for item in representation.Items:
                    if not item.is_a("IfcStyledItem"):
                        continue
                    current_styles: list[ifcopenshell.entity_instance] = list(item.Styles)
                    while current_styles:
                        style = current_styles.pop()
                        if style.is_a("IfcPresentationStyleAssignment"):
                            current_styles.extend(style.Styles)
                            continue
                        results.append(
                            {
                                "context_type": context.ContextType,
                                "context_identifier": getattr(context, "ContextIdentifier", ""),
                                "target_view": getattr(context, "TargetView", ""),
                                "name": style.Name or "Unnamed",
                                "id": style.id(),
                                "context_id": context.id(),
                            }
                        )
        return results


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
        cls.data["material_type"] = cls.material_type()
        cls.data["active_material_constituents"] = cls.active_material_constituents()
        # after material_name and type_material
        cls.data["is_type_material_overridden"] = cls.is_type_material_overridden()

        cls.is_loaded = True

    @classmethod
    def material_class(cls) -> Union[str, None]:
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
            if cls.material.is_a("IfcMaterialLayerSetUsage"):
                if cls.material.LayerSetDirection:
                    results["layer_set_direction"] = cls.material.LayerSetDirection

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
            elif cls.material.is_a("IfcMaterialList"):
                items = cls.material.Materials

            icon = "LAYER_ACTIVE"
            if "Layer" in cls.material.is_a():
                icon = "ALIGN_CENTER"
            elif "Profile" in cls.material.is_a():
                icon = "ITALIC"
            elif "Constituent" in cls.material.is_a():
                icon = "POINTCLOUD_DATA"

            for item in items or []:
                if item.is_a("IfcMaterial"):
                    material_id = item.id()
                else:
                    material_id = item.Material.id()
                data = {
                    "id": item.id(),
                    "name": getattr(item, "Name", None) or "Unnamed",
                    "icon": icon,
                    "material_id": material_id,
                }
                if item.is_a("IfcMaterialProfile") and not item.Name:
                    if item.Profile:
                        data["name"] = item.Profile.ProfileName or "Unnamed"
                    else:
                        data["name"] = "No Profile"
                if item.is_a("IfcMaterialLayer"):
                    total_thickness = item.LayerThickness
                    unit_system = bpy.context.scene.unit_settings.system
                    if unit_system == "IMPERIAL":
                        precision = bpy.context.scene.DocProperties.imperial_precision
                    else:
                        precision = None
                    formatted_thickness = format_distance(
                        total_thickness, precision=precision, suppress_zero_inches=True, in_unit_length=True
                    )
                    data["name"] = f"{formatted_thickness} - {data['name']}"
                if item.is_a("IfcMaterial"):
                    data["material"] = item.Name or "Unnamed"
                else:
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
    def set_item_name(cls) -> Union[str, None]:
        if cls.material:
            material_class = cls.material.is_a()
            if "Constituent" in material_class:
                return "constituent"
            elif "Layer" in material_class:
                return "layer"
            elif "Profile" in material_class:
                return "profile"
            elif "List" in material_class:
                return "list_item"

    @classmethod
    def material_name(cls) -> Union[str, None]:
        material = cls.material
        if material:
            return getattr(material, "Name", None) or "Unnamed"

    @classmethod
    def materials(cls) -> list[tool.Blender.BLENDER_ENUM_ITEM]:
        is_ifc2x3 = tool.Ifc.get_schema() == "IFC2X3"
        return sorted(
            [
                (str(m.id()), m.Name or "Unnamed", "" if is_ifc2x3 else (m.Description or ""))
                for m in tool.Ifc.get().by_type("IfcMaterial")
            ],
            key=lambda x: x[1],
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

    @classmethod
    def material_type(cls):
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
    def active_material_constituents(cls):
        material = cls.material
        if not cls.material or not material.is_a("IfcMaterialConstituentSet"):
            return []
        return [m.Name for m in material.MaterialConstituents if m.Name]

    @classmethod
    def is_type_material_overridden(cls) -> bool:
        if not cls.data["type_material"]:
            return False

        # try to avoid accessing ifc
        if cls.data["material_name"] != cls.data["type_material"]:
            return True

        # in theory material can be overridden by the same material
        # so we check occurrence material explicitly
        element = tool.Ifc.get_entity(bpy.context.active_object)
        occurrence_material = ifcopenshell.util.element.get_material(element, should_inherit=False)
        return bool(occurrence_material) and "Usage" not in occurrence_material.is_a()
