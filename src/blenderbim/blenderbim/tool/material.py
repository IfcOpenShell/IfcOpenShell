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

from __future__ import annotations
import bpy
import ifcopenshell
import blenderbim.core.tool
import blenderbim.core.material
import blenderbim.tool as tool
import blenderbim.bim.helper
import ifcopenshell.util.unit
import ifcopenshell.util.element
from collections import defaultdict
from typing import Union, Any, TYPE_CHECKING

if TYPE_CHECKING:
    # Avoid circular imports.
    from blenderbim.bim.module.material.prop import Material as MaterialItem


class Material(blenderbim.core.tool.Material):
    @classmethod
    def add_default_material_object(cls, name: Union[str, None]) -> bpy.types.Material:
        return bpy.data.materials.new(name or "Default")

    @classmethod
    def delete_object(cls, obj: bpy.types.Material) -> None:
        bpy.data.materials.remove(obj)

    @classmethod
    def disable_editing_materials(cls) -> None:
        bpy.context.scene.BIMMaterialProperties.is_editing = False

    @classmethod
    def enable_editing_materials(cls) -> None:
        bpy.context.scene.BIMMaterialProperties.is_editing = True

    @classmethod
    def get_active_material_type(cls) -> str:
        return bpy.context.scene.BIMMaterialProperties.material_type

    @classmethod
    def get_elements_by_material(cls, material: ifcopenshell.entity_instance) -> list[ifcopenshell.entity_instance]:
        return ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)

    @classmethod
    def get_name(cls, obj: bpy.types.Material) -> str:
        return obj.name

    @classmethod
    def get_active_material_item(cls) -> Union[MaterialItem, None]:
        """Get active material props item if index is valid, otherwise, return None."""
        props = bpy.context.scene.BIMMaterialProperties
        if 0 <= props.active_material_index < len(props.materials):
            return props.materials[props.active_material_index]
        return None

    @classmethod
    def import_material_definitions(cls, material_type: str) -> None:
        props = bpy.context.scene.BIMMaterialProperties

        # Store active category name to reselect it later.
        # Occurs when we expand/contract all categories.
        active_item = cls.get_active_material_item()
        previously_selected_category = None
        if active_item and active_item.is_category:
            previously_selected_category = active_item.name

        expanded_categories = {m.name for m in props.materials if m.is_category and m.is_expanded}
        props.materials.clear()
        get_name = lambda x: x.Name or "Unnamed"
        if material_type == "IfcMaterialLayerSet":
            get_name = lambda x: x.LayerSetName or "Unnamed"
        elif material_type == "IfcMaterialList":
            get_name = lambda x: "Unnamed"
        materials = sorted(tool.Ifc.get().by_type(material_type), key=get_name)
        categories = defaultdict(list)
        if material_type == "IfcMaterial":
            category_index_to_reselect = None

            for m in materials:
                # IfcMaterial has Category since IFC4.
                category = getattr(m, "Category", None)
                category = category or "Uncategorised"
                categories[category].append(m)

            for category, mats in categories.items():
                cat = props.materials.add()
                cat.name = category
                cat.is_category = True
                cat.is_expanded = cat.name in expanded_categories

                if previously_selected_category == category:
                    category_index_to_reselect = len(props.materials) - 1

                for material in mats if cat.is_expanded else []:
                    new = props.materials.add()
                    new.ifc_definition_id = material.id()
                    new.name = get_name(material)
                    new.total_elements = len(
                        ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
                    )
                    new.has_style = bool(material.HasRepresentation)

            if category_index_to_reselect is not None:
                props.active_material_index = category_index_to_reselect
            return
        for material in materials:
            new = props.materials.add()
            new.ifc_definition_id = material.id()
            new.name = get_name(material)
            new.total_elements = len(ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material))

    @classmethod
    def is_editing_materials(cls) -> bool:
        return bpy.context.scene.BIMMaterialProperties.is_editing

    @classmethod
    def is_material_used_in_sets(cls, material: ifcopenshell.entity_instance) -> bool:
        for inverse in tool.Ifc.get().get_inverse(material):
            if inverse.is_a() in [
                "IfcMaterialProfile",
                "IfcMaterialLayer",
                "IfcMaterialConstituent",
                "IfcMaterialList",
            ]:
                return True
        return False

    @classmethod
    def load_material_attributes(cls, material: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMMaterialProperties
        props.material_attributes.clear()
        blenderbim.bim.helper.import_attributes2(material, props.material_attributes)

    @classmethod
    def enable_editing_material(cls, material: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = material.id()
        props.editing_material_type = "ATTRIBUTES"

    @classmethod
    def get_material_attributes(cls) -> dict[str, Any]:
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMMaterialProperties.material_attributes)

    @classmethod
    def disable_editing_material(cls) -> None:
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = 0
        props.editing_material_type = ""

    @classmethod
    def get_type(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_active_object_material(cls) -> Union[str, None]:
        active_obj = bpy.context.active_object
        if not active_obj:
            return
        return active_obj.BIMObjectMaterialProperties.material_type

    @classmethod
    def get_active_material(cls) -> ifcopenshell.entity_instance:
        return tool.Ifc.get().by_id(int(bpy.context.active_object.BIMObjectMaterialProperties.material))

    @classmethod
    def get_material(
        cls, element: ifcopenshell.entity_instance, should_inherit: bool = False
    ) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_material(element, should_inherit=should_inherit)

    @classmethod
    def is_a_material_set(cls, material: ifcopenshell.entity_instance) -> bool:
        return material.is_a() in [
            "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet",
            "IfcMaterialProfileSet",
        ]

    @classmethod
    def add_material_to_set(
        cls, material_set: ifcopenshell.entity_instance, material: ifcopenshell.entity_instance
    ) -> None:
        if material_set.is_a("IfcMaterialConstituentSet"):
            if not material_set.MaterialConstituents:
                tool.Ifc.run(
                    "material.add_constituent",
                    constituent_set=material_set,
                    material=material,
                )
        elif material_set.is_a() == "IfcMaterialLayerSet":
            if not material_set.MaterialLayers:
                unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                layer = tool.Ifc.run(
                    "material.add_layer",
                    layer_set=material_set,
                    material=material,
                )
                thickness = 0.1  # Arbitrary metric thickness for now
                layer.LayerThickness = thickness / unit_scale
        elif material_set.is_a("IfcMaterialProfileSet"):
            if not material_set.MaterialProfiles:
                named_profiles = [p for p in tool.Ifc.get().by_type("IfcProfileDef") if p.ProfileName]
                if named_profiles:
                    profile = named_profiles[0]
                else:
                    unit_scale = ifcopenshell.util.unit.calculate_unit_scale(tool.Ifc.get())
                    size = 0.5 / unit_scale
                    profile = tool.Ifc.get().create_entity(
                        "IfcRectangleProfileDef",
                        ProfileName="New Profile",
                        ProfileType="AREA",
                        XDim=size,
                        YDim=size,
                    )
                    material_profile = tool.Ifc.run(
                        "material.add_profile",
                        profile_set=material_set,
                        material=material,
                        profile=profile,
                    )

    @classmethod
    def has_material_profile(cls, element: ifcopenshell.entity_instance) -> bool:
        material = cls.get_material(element, should_inherit=False)
        inherited_material = cls.get_material(element, should_inherit=True)
        if material and "Profile" in material.is_a():
            return True
        if inherited_material and "Profile" in inherited_material.is_a():
            return True
        return False

    @classmethod
    def is_a_flow_segment(cls, element: ifcopenshell.entity_instance) -> bool:
        return element.is_a("IfcFlowSegment")

    @classmethod
    def replace_material_with_material_profile(
        cls, element: ifcopenshell.entity_instance
    ) -> ifcopenshell.entity_instance:
        old_material = cls.get_material(element, should_inherit=False)
        old_inherited_material = cls.get_material(element, should_inherit=True)
        material = old_material if old_material and old_material.is_a("IfcMaterial") else None
        if not material and old_inherited_material:
            material = old_inherited_material if old_inherited_material.is_a("IfcMaterial") else None
        if not material:
            material = tool.Ifc.get().by_type("IfcMaterial")[0]
        else:
            blenderbim.core.material.unassign_material(tool.Ifc, tool.Material, objects=[tool.Ifc.get_object(element)])
        tool.Ifc.run("material.assign_material", products=[element], type="IfcMaterialProfileSet", material=material)
        assinged_material = cls.get_material(element)
        material_profile = tool.Ifc.run("material.add_profile", profile_set=assinged_material, material=material)
        return material_profile

    @classmethod
    def update_elements_using_material(cls, material: ifcopenshell.entity_instance) -> None:
        # update elements that are using this material
        elements = ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
        objects = [tool.Ifc.get_object(e) for e in elements]
        tool.Geometry.reload_representation(objects)

    @classmethod
    def sync_blender_material_name(cls, material: ifcopenshell.entity_instance) -> None:
        name = material.Name or "Unnamed"
        obj = tool.Ifc.get_object(material)
        if obj:
            obj.name = name
        style = tool.Style.get_style(obj)
        if style:
            style.Name = name
            obj = tool.Ifc.get_object(style)
            if obj:
                obj.name = name

    @classmethod
    def get_style(cls, material: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for material_representation in material.HasRepresentation:
            for representation in material_representation.Representations:
                for item in representation.Items:
                    for style in item.Styles:
                        if style.is_a("IfcSurfaceStyle"):
                            return style
