# IfcOpenShell - IFC toolkit and geometry engine
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of IfcOpenShell.
#
# IfcOpenShell is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# IfcOpenShell is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with IfcOpenShell.  If not, see <http://www.gnu.org/licenses/>.

import ifcopenshell
import ifcopenshell.api
import ifcopenshell.util.element
import ifcopenshell.util.representation


class Usecase:
    def __init__(self, file, product=None, type="IfcMaterial", material=None):
        """Assigns a material to a product

        When a material is assigned to a product, it means that the product is
        made out of that material. In its simplest form, a single material may
        be assigned to a product, meaning that the entire product is made out of
        that one material. Alternatively, a material set may be assigned to a
        product, meaning that the product is made out of a set of materials.
        There are three types of sets, including layered construction, profiled
        materials, and arbitrary material constituents. See
        ifcopenshell.api.material.add_material_set for details.

        Materials are typically assigned to the element types rather than
        individual occurrences of elements. Individual occurrences would then
        inherit the material from the type.

        If the type has a material set, then the geometry of the occurrences
        must comply with the material set. For example, if the type has a
        constituent set, then it is expected that all occurrences also inherit
        the geometry of the type, which is made out of those constituents.
        Alternatively, if the type has a layer set, then all occurrences must
        have geometry that has a thickness equal to the sum of all layers. If a
        type has a profile set, then all occurrences must has the same profile
        extruded along its axis.

        For layers and profiles assigned to types, the occurrences must be
        assigned an IfcMaterialLayerSetUsage or an IfcMaterialProfileSetUsage.
        This allows individual occurrences to override the layered or profiled
        construction offset from a reference line.

        :param product: The IfcProduct to assign the material or material set
            to.
        :type product: ifcopenshell.entity_instance.entity_instance
        :param type: Choose from "IfcMaterial", "IfcMaterialConstituentSet",
            "IfcMaterialLayerSet", "IfcMaterialLayerSetUsage",
            "IfcMaterialProfileSet", "IfcMaterialProfileSetUsage", or
            "IfcMaterialList". Note that "Set Usages" may only be assigned to
            occurrences, not types.
        :type type: str
        :param material: The IfcMaterial or material set you are assigning here.
        :type material: ifcopenshell.entity_instance.entity_instance
        :return: The IfcRelAssociatesMaterial entity
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Let's start with a simple concrete material
            concrete = ifcopenshell.api.run("material.add_material", model, name="CON01", category="concrete")

            # Let's imagine a concrete bench made out of a single concrete
            # material. Let's assign it to the type.
            bench_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurnitureType")
            ifcopenshell.api.run("material.assign_material", model,
                product=bench_type, type="IfcMaterial", material=concrete)

            # Let's imagine there are a two occurrences of this bench.  It's not
            # necessary to assign any material to these benches as they
            # automatically inherit the material from the type.
            bench1 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")
            bench2 = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcFurniture")
            ifcopenshell.api.run("type.assign_type", model, related_object=bench1, relating_type=bench_type)
            ifcopenshell.api.run("type.assign_type", model, related_object=bench2, relating_type=bench_type)

            # If we have a concrete wall, we should use a layer set. Again,
            # let's start with a wall type, not occurrences.
            wall_type = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWallType", name="WAL01")

            # Even though there is only one layer in our layer set, we still use
            # a layer set because it makes it clear that this is a layered
            # construction. Let's say it's a 200mm thick concrete layer.
            material_set = ifcopenshell.api.run("material.add_material_set", model,
                name="CON200", set_type="IfcMaterialLayerSet")
            layer = ifcopenshell.api.run("material.add_layer", model, layer_set=material_set, material=steel)
            ifcopenshell.api.run("material.edit_layer", model, layer=layer, attributes={"LayerThickness": 200})

            # Our wall type now has the layer set assigned to it
            ifcopenshell.api.run("material.assign_material", model,
                product=wall_type, type="IfcMaterialLayerSet", material=material_set)

            # Let's imagine an occurrence of this wall type.
            wall = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcWall")
            ifcopenshell.api.run("type.assign_type", model, related_object=wall, relating_type=wall_type)

            # Our wall occurrence needs to have a "set usage" which describes
            # how the layers relate to a reference line (typically a 2D line
            # representing the extents of the wall). Usages are special since
            # they automatically detect the inherited material set from the
            # type. You'd write similar code for a profile set.
            ifcopenshell.api.run("material.assign_material", model,
                product=wall, type="IfcMaterialLayerSetUsage")

            # To be complete, let's create the wall's axis and body
            # representation. Notice how the axis guides the walls "reference
            # line" which determines where layers are extruded from, and the
            # body has a thickness of 200mm, same as our total layer set
            # thickness.
            axis = ifcopenshell.api.run("geometry.add_axis_representation", model,
                context=axis_context, axis=[(0.0, 0.0), (5000.0, 0.0)])
            body = ifcopenshell.api.run("geometry.add_wall_representation", model,
                context=body_context, length=5000, height=3000, thickness=200)
            ifcopenshell.api.run("geometry.assign_representation", model, product=wall, representation=axis)
            ifcopenshell.api.run("geometry.assign_representation", model, product=wall, representation=body)
            ifcopenshell.api.run("geometry.edit_object_placement", model, product=wall)
        """
        self.file = file
        self.settings = {"product": product, "type": type, "material": material}

    def execute(self):
        material = ifcopenshell.util.element.get_material(self.settings["product"])
        if material:
            ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["product"])
        if self.settings["type"] == "IfcMaterial" or (
            self.settings["material"] and not self.settings["material"].is_a("IfcMaterial")
        ):
            return self.assign_ifc_material()
        elif self.settings["type"] == "IfcMaterialConstituentSet":
            material_set = self.file.create_entity(self.settings["type"])
            return self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialLayerSet":
            material_set = self.file.create_entity(self.settings["type"])
            return self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialLayerSetUsage":
            element_type = ifcopenshell.util.element.get_type(self.settings["product"])
            if element_type:
                element_type_material = ifcopenshell.util.element.get_material(element_type)
                if element_type_material and element_type_material.is_a("IfcMaterialLayerSet"):
                    material_set = element_type_material
                else:
                    material_set = self.file.create_entity("IfcMaterialLayerSet")
            else:
                material_set = self.file.create_entity("IfcMaterialLayerSet")
            material_set_usage = self.create_layer_set_usage(material_set)
            return self.create_material_association(material_set_usage)
        elif self.settings["type"] == "IfcMaterialProfileSet":
            material_set = self.file.create_entity(self.settings["type"])
            return self.create_material_association(material_set)
        elif self.settings["type"] == "IfcMaterialProfileSetUsage":
            element_type = ifcopenshell.util.element.get_type(self.settings["product"])
            if element_type:
                element_type_material = ifcopenshell.util.element.get_material(element_type)
                if element_type_material and element_type_material.is_a("IfcMaterialProfileSet"):
                    material_set = element_type_material
                else:
                    material_set = self.file.create_entity("IfcMaterialProfileSet")
            else:
                material_set = self.file.create_entity("IfcMaterialProfileSet")

            self.update_representation_profile(material_set)
            material_set_usage = self.create_profile_set_usage(material_set)
            return self.create_material_association(material_set_usage)
        elif self.settings["type"] == "IfcMaterialList":
            material_set = self.file.create_entity(self.settings["type"])
            material_set.Materials = [self.settings["material"]]
            return self.create_material_association(material_set)

    def update_representation_profile(self, material_set):
        profile = material_set.CompositeProfile
        if not profile and material_set.MaterialProfiles:
            profile = material_set.MaterialProfiles[0].Profile
        if not profile:
            return
        representation = ifcopenshell.util.representation.get_representation(
            self.settings["product"], "Model", "Body", "MODEL_VIEW"
        )
        if not representation:
            return
        for subelement in self.file.traverse(representation):
            if subelement.is_a("IfcSweptAreaSolid"):
                subelement.SweptArea = profile

    def create_layer_set_usage(self, material_set):
        if self.settings["product"].is_a() in [
            "IfcSlab",
            "IfcSlabStandardCase",
            "IfcSlabElementedCase",
            "IfcRoof",
            "IfcRamp",
            "IfcPlate",
            "IfcPlateStandardCase",
        ]:
            layer_set_direction = "AXIS3"
        else:
            layer_set_direction = "AXIS2"
        return self.file.create_entity(
            "IfcMaterialLayerSetUsage",
            **{
                "ForLayerSet": material_set,
                "LayerSetDirection": layer_set_direction,
                "DirectionSense": "POSITIVE",
                "OffsetFromReferenceLine": 0,
            }
        )

    def create_profile_set_usage(self, material_set):
        return self.file.create_entity("IfcMaterialProfileSetUsage", **{"ForProfileSet": material_set})

    def assign_ifc_material(self):
        rel = self.get_rel_associates_material(self.settings["material"])
        if not rel:
            return self.create_material_association(self.settings["material"])
        related_objects = list(rel.RelatedObjects)
        related_objects.append(self.settings["product"])
        rel.RelatedObjects = related_objects
        return rel

    def create_material_association(self, relating_material):
        return self.file.create_entity(
            "IfcRelAssociatesMaterial",
            **{
                "GlobalId": ifcopenshell.guid.new(),
                "RelatedObjects": [self.settings["product"]],
                "RelatingMaterial": relating_material,
            }
        )

    def get_rel_associates_material(self, material):
        if self.file.schema == "IFC2X3" or material.is_a("IfcMaterialList"):
            rel = [
                r
                for r in self.file.by_type("IfcRelAssociatesMaterial")
                if r.RelatingMaterial == self.settings["material"]
            ]
            return rel[0] if rel else None
        if self.settings["material"].AssociatedTo:
            return self.settings["material"].AssociatedTo[0]
