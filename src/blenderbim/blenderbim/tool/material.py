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
import blenderbim.core.tool
import blenderbim.tool as tool
import blenderbim.bim.helper
import ifcopenshell.util.unit
import ifcopenshell.util.element


class Material(blenderbim.core.tool.Material):
    @classmethod
    def add_default_material_object(cls, name):
        return bpy.data.materials.new(name or "Default")

    @classmethod
    def delete_object(cls, obj):
        bpy.data.materials.remove(obj)

    @classmethod
    def disable_editing_materials(cls):
        bpy.context.scene.BIMMaterialProperties.is_editing = False

    @classmethod
    def duplicate_material(cls, material: ifcopenshell.entity_instance) -> ifcopenshell.entity_instance:
        new_material = ifcopenshell.util.element.copy_deep(tool.Ifc.get(), material)
        new_material.Name = material.Name + "_copy"
        return new_material

    @classmethod
    def enable_editing_materials(cls):
        bpy.context.scene.BIMMaterialProperties.is_editing = True

    @classmethod
    def get_active_material_type(cls):
        return bpy.context.scene.BIMMaterialProperties.material_type

    @classmethod
    def get_elements_by_material(cls, material):
        return ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)

    @classmethod
    def get_name(cls, obj):
        return obj.name

    @classmethod
    def import_material_definitions(cls, material_type):
        props = bpy.context.scene.BIMMaterialProperties
        expanded_categories = {m.name for m in props.materials if m.is_expanded}
        props.materials.clear()
        get_name = lambda x: x.Name or "Unnamed"
        if material_type == "IfcMaterialLayerSet":
            get_name = lambda x: x.LayerSetName or "Unnamed"
        elif material_type == "IfcMaterialList":
            get_name = lambda x: "Unnamed"
        materials = sorted(tool.Ifc.get().by_type(material_type), key=get_name)
        categories = {}
        if material_type == "IfcMaterial":
            [categories.setdefault(getattr(m, "Category", "Uncategorised"), []).append(m) for m in materials]
            for category, mats in categories.items():
                cat = props.materials.add()
                cat.name = category or ""
                cat.is_category = True
                cat.is_expanded = cat.name in expanded_categories
                for material in mats if cat.is_expanded else []:
                    new = props.materials.add()
                    new.ifc_definition_id = material.id()
                    new.name = get_name(material)
                    new.total_elements = len(
                        ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
                    )
                    new.has_style = bool(material.HasRepresentation)
            return
        for material in materials:
            new = props.materials.add()
            new.ifc_definition_id = material.id()
            new.name = get_name(material)
            new.total_elements = len(ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material))

    @classmethod
    def is_editing_materials(cls):
        return bpy.context.scene.BIMMaterialProperties.is_editing

    @classmethod
    def is_material_used_in_sets(cls, material):
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
    def load_material_attributes(cls, material):
        props = bpy.context.scene.BIMMaterialProperties
        props.material_attributes.clear()
        blenderbim.bim.helper.import_attributes2(material, props.material_attributes)

    @classmethod
    def enable_editing_material(cls, material):
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = material.id()
        props.editing_material_type = "ATTRIBUTES"

    @classmethod
    def get_material_attributes(cls):
        return blenderbim.bim.helper.export_attributes(bpy.context.scene.BIMMaterialProperties.material_attributes)

    @classmethod
    def disable_editing_material(cls):
        props = bpy.context.scene.BIMMaterialProperties
        props.active_material_id = 0
        props.editing_material_type = ""

    @classmethod
    def get_type(cls, element):
        return ifcopenshell.util.element.get_type(element)

    @classmethod
    def get_active_object_material(cls):
        active_obj = bpy.context.active_object
        if not active_obj:
            return
        return active_obj.BIMObjectMaterialProperties.material_type

    @classmethod
    def get_active_material(cls):
        return tool.Ifc.get().by_id(int(bpy.context.active_object.BIMObjectMaterialProperties.material))

    @classmethod
    def get_material(cls, element, should_inherit=False):
        return ifcopenshell.util.element.get_material(element, should_inherit=should_inherit)

    @classmethod
    def is_a_material_set(cls, material):
        return material.is_a() in [
            "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet",
            "IfcMaterialProfileSet",
        ]

    @classmethod
    def add_material_to_set(cls, material_set, material):
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
    def has_material_profile(cls, element):
        material = cls.get_material(element, should_inherit=False)
        inherited_material = cls.get_material(element, should_inherit=True)
        if material and "Profile" in material.is_a():
            return True
        if inherited_material and "Profile" in inherited_material.is_a():
            return True
        return False

    @classmethod
    def is_a_flow_segment(cls, element):
        return element.is_a("IfcFlowSegment")

    @classmethod
    def replace_material_with_material_profile(cls, element):
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
    def update_elements_using_material(cls, material):
        # update elements that are using this material
        elements = ifcopenshell.util.element.get_elements_by_material(tool.Ifc.get(), material)
        # filter only unique representations to avoid reloading same representations multiple times
        meshes_to_objects = dict()
        for e in elements:
            obj = tool.Ifc.get_object(e)
            mesh = obj.data
            meshes_to_objects[mesh] = obj
        for obj in meshes_to_objects.values():
            tool.Geometry.reload_representation(obj)
