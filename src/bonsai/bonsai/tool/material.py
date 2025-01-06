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

from __future__ import annotations
import bpy
import ifcopenshell
import ifcopenshell.api.material
import bonsai.core.tool
import bonsai.core.material
import bonsai.tool as tool
import bonsai.bim.helper
import ifcopenshell.util.unit
import ifcopenshell.util.element
from collections import defaultdict
from typing import Union, Any, TYPE_CHECKING, Optional, Literal
from typing_extensions import assert_never

if TYPE_CHECKING:
    # Avoid circular imports.
    from bonsai.bim.module.material.prop import Material as MaterialItem


class Material(bonsai.core.tool.Material):
    @classmethod
    def disable_editing_materials(cls) -> None:
        bpy.context.scene.BIMMaterialProperties.is_editing = False

    @classmethod
    def duplicate_material(cls, material: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        new = tool.Ifc.run("material.copy_material", material=material)

        # Doesn't have a name.
        if new.is_a("IfcMaterialList"):
            return new

        name_index = 1 if new.is_a("IfcMaterialLayerSet") else 0
        name = (new[name_index] or "Unnamed") + " Copy"
        new[name_index] = name
        return new

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
    def get_active_material_item(cls) -> Union[MaterialItem, None]:
        """Get active material props item if index is valid, otherwise, return None."""
        props = bpy.context.scene.BIMMaterialProperties
        if 0 <= props.active_material_index < len(props.materials):
            return props.materials[props.active_material_index]
        return None

    @classmethod
    def get_material_category(cls, material: ifcopenshell.entity_instance) -> str:
        # IfcMaterial has Category since IFC4.
        return getattr(material, "Category", None) or "Uncategorised"

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
                category = cls.get_material_category(m)
                categories[category].append(m)

            for category, mats in categories.items():
                cat = props.materials.add()
                cat["name"] = category
                cat.is_category = True
                cat.is_expanded = cat.name in expanded_categories

                if previously_selected_category == category:
                    category_index_to_reselect = len(props.materials) - 1

                for material in mats if cat.is_expanded else []:
                    new = props.materials.add()
                    new["name"] = get_name(material)
                    new.ifc_definition_id = material.id()
                    new.total_elements = len(
                        ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
                    )
                    new.has_style = bool(material.HasRepresentation)

            if category_index_to_reselect is not None:
                props.active_material_index = category_index_to_reselect
        else:
            for material in materials:
                new = props.materials.add()
                new["name"] = get_name(material)
                new.ifc_definition_id = material.id()
                new.total_elements = len(ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material))

        from bonsai.bim.module.material.data import MaterialsData

        MaterialsData.data["material_styles_data"] = MaterialsData.material_styles_data()

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
        bonsai.bim.helper.import_attributes2(material, props.material_attributes)

    @classmethod
    def enable_editing_material(cls, material: ifcopenshell.entity_instance) -> None:
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = material.id()
        props.editing_material_type = "ATTRIBUTES"

    @classmethod
    def get_material_attributes(cls) -> dict[str, Any]:
        return bonsai.bim.helper.export_attributes(bpy.context.scene.BIMMaterialProperties.material_attributes)

    @classmethod
    def disable_editing_material(cls) -> None:
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = 0
        props.editing_material_type = ""

    @classmethod
    def get_default_material(cls) -> ifcopenshell.entity_instance:
        """Return first found IfcMaterial in IFC file or create a new default material."""
        ifc_file = tool.Ifc.get()
        material = next(iter(ifc_file.by_type("IfcMaterial")), None)
        if material:
            return material
        material = ifcopenshell.api.material.add_material(ifc_file, name="Default")
        return material

    @classmethod
    def get_type(cls, element: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_object_ui_material_type(cls) -> str:
        active_obj = bpy.context.active_object
        return active_obj.BIMObjectMaterialProperties.material_type

    @classmethod
    def get_object_ui_active_material(cls) -> ifcopenshell.entity_instance:
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
            bonsai.core.material.unassign_material(tool.Ifc, tool.Material, objects=[tool.Ifc.get_object(element)])
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
    def get_style(cls, material: ifcopenshell.entity_instance) -> Union[ifcopenshell.entity_instance, None]:
        for material_representation in material.HasRepresentation:
            for representation in material_representation.Representations:
                for item in representation.Items:
                    for style in item.Styles:
                        if style.is_a("IfcSurfaceStyle"):
                            return style

    @classmethod
    def ensure_material_unassigned(cls, elements: list[ifcopenshell.entity_instance]) -> None:
        """Ensure blender materials are updated after a material unassignment.

        E.g. during a material unassignment some material style may not apply anymore
        or some other may be applied now since it's no longer overridden,
        therefore we need to make sure blender materials reflect correct styles.

        Designed to be called after material.unassign_material API call."""
        elements = elements.copy()  # Avoid argument mutation.
        for element in elements[:]:
            if element.is_a("IfcElementType"):
                elements.extend(tool.Model.get_occurrences_without_material_override(element))
        tool.Model.apply_ifc_material_changes(elements)

    @classmethod
    def ensure_material_assigned(
        cls,
        elements: list[ifcopenshell.entity_instance],
        material_type: ifcopenshell.util.element.MATERIAL_TYPE = "IfcMaterial",
        material: Optional[ifcopenshell.entity_instance] = None,
    ) -> None:
        """Ensure blender materials are updated after a material assignment.

        Designed to be called after material.assign_material API call.
        For material sets it should be called after some item is already added to the material set."""

        # NOTE: adding/editing/removing layers/profiles/constituents is not supported.
        # Adding support for profiles/layers it only will be possible when we'll be adding styles
        # to the representations generated from layer and profile sets.

        if material:
            assigned_material = material
        else:
            element = elements[0]
            if material_type == "IfcMaterial":
                assigned_material = ifcopenshell.util.element.get_material(element, should_inherit=False)
                assert assigned_material  # Type checker.
            # Material usages just inherit the style from the type material, so can't override it.
            elif material_type in ("IfcMaterialLayerSetUsage", "IfcMaterialProfileSetUsage"):
                return
            # If type is Set and no material argument were provided, then Set was just created
            # and not yet have any IfcMaterials.
            elif material_type in ("IfcMaterialConstituentSet", "IfcMaterialLayerSet", "IfcMaterialProfileSet"):
                return
            elif material_type == "IfcMaterialList":
                assert False, "Current assign_material implementation requires 'material' argument for IfcMaterialList."
            else:
                assert False, f"Invalid material type found: {material_type}"

        for element in elements[:]:
            if element.is_a("IfcElementType"):
                elements.extend(tool.Model.get_occurrences_without_material_override(element))

        tool.Model.apply_ifc_material_changes(elements, assigned_material=assigned_material)

    @classmethod
    def ensure_new_material_set_is_valid(cls, material: ifcopenshell.entity_instance) -> None:
        material_type = material.is_a()

        ifc_file = tool.Ifc.get()
        default_material = cls.get_default_material()

        if material_type == "IfcMaterialConstituentSet":
            material_constituent = ifcopenshell.api.material.add_constituent(
                ifc_file,
                constituent_set=material,
                material=default_material,
            )
            material.MaterialConstituents = [material_constituent]
        elif material_type == "IfcMaterialLayerSet":
            material_layer = ifcopenshell.api.material.add_layer(
                ifc_file,
                layer_set=material,
                material=default_material,
            )
            material.MaterialLayers = [material_layer]
        elif material_type == "IfcMaterialProfileSet":
            profile = tool.Profile.get_default_profile()
            material_profile = ifcopenshell.api.material.add_profile(
                ifc_file,
                profile_set=material,
                profile=profile,
                material=None,
            )
            material.MaterialProfiles = [material_profile]
        elif material_type == "IfcMaterialList":
            material.Materials = [default_material]
        else:
            assert False, f"Invalid material type found: {material_type}."

    @classmethod
    def purge_unused_materials(cls) -> int:
        ifc_file = tool.Ifc.get()
        is_ifc2x3 = ifc_file.schema == "IFC2X3"
        ifc_class = "IfcMaterial" if is_ifc2x3 else "IfcMaterialDefinition"

        skip_inverses = {
            "IfcMaterialDefinitionRepresentation",
            "IfcMaterialProperties",
        }

        def is_safe_to_purge(material: ifcopenshell.entity_instance) -> bool:
            for i in ifc_file.get_inverse(material):
                if i.is_a() not in skip_inverses:
                    return False
            return True

        materials = ifc_file.by_type(ifc_class)
        # Not IfcMaterialDefinition...
        materials += ifc_file.by_type("IfcMaterialList")
        # In IFC2X3 materials don't have a common class.
        if is_ifc2x3:
            materials += ifc_file.by_type("IfcMaterialLayer")
            materials += ifc_file.by_type("IfcMaterialLayerSet")
            materials += ifc_file.by_type("IfcMaterialLayerSetUsage")

        i = 0
        for material in materials:
            if ifc_file.get_total_inverses(material) != 0 and not is_safe_to_purge(material):
                continue
            ifcopenshell.api.material.remove_material(ifc_file, material)
            i += 1

        if i == 0:
            return 0

        i += cls.purge_unused_materials()
        return i

    @classmethod
    def get_material_name(cls, material: ifcopenshell.entity_instance) -> Union[str, None]:
        ifc_class = material.is_a()
        if ifc_class == "IfcMaterialList":
            return None
        elif ifc_class == "IfcMaterialLayerSet":
            # Optional IfcLabel.
            return material.LayerSetName
        # Optional IfcLabel except for IfcMaterial.
        return material.Name
