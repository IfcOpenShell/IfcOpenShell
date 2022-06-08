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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"product": None, "type": "IfcMaterial", "material": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        material = ifcopenshell.util.element.get_material(self.settings["product"])
        if material:
            ifcopenshell.api.run("material.unassign_material", self.file, product=self.settings["product"])
        if self.settings["type"] == "IfcMaterial":
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
