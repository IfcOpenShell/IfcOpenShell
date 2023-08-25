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
import ifcopenshell.api.owner.settings


class Usecase:
    def __init__(self, file, library=None, element=None):
        """Appends an asset from a library into the active project

        A BIM library asset may be a type product (e.g. wall type), product
        (e.g. pump), material, profile, or cost schedule.

        This copies the asset from the specified library file into the active
        project. It handles all details like ensuring that product materials,
        styles, properties, quantities, and so on are preserved.

        If an asset contains geometry, the geometric contexts are also
        intelligentely transplanted such that existing equivalent contexts are
        reused.

        Do not mix units.

        :param library: The file object containing the asset.
        :type library: ifcopenshell.file.file
        :param element: An element in the library file of the asset. It may be
            an IfcTypeProduct, IfcProduct, IfcMaterial, IfcCostSchedule, or
            IfcProfileDef.
        :type library: ifcopenshell.entity_instance.entity_instance
        :return: The appended element
        :rtype: ifcopenshell.entity_instance.entity_instance

        Example:

        .. code:: python

            # Programmatically generate a library. You could do this visually too.
            library = ifcopenshell.api.run("project.create_file")
            root = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcProject", name="Demo Library")
            context = ifcopenshell.api.run("root.create_entity", library,
                ifc_class="IfcProjectLibrary", name="Demo Library")
            ifcopenshell.api.run("project.assign_declaration", library, definition=context, relating_context=root)

            # Assign units for our example library
            unit = ifcopenshell.api.run("unit.add_si_unit", library,
                unit_type="LENGTHUNIT", name="METRE", prefix="MILLI")
            ifcopenshell.api.run("unit.assign_unit", library, units=[unit])

            # Let's create a single asset of a 200mm thick concrete wall
            wall_type = ifcopenshell.api.run("root.create_entity", library, ifc_class="IfcWallType", name="WAL01")
            concrete = ifcopenshell.api.run("material.add_material", self.file, name="CON", category="concrete")
            rel = ifcopenshell.api.run("material.assign_material", library,
                product=wall_type, type="IfcMaterialLayerSet")
            layer = ifcopenshell.api.run("material.add_layer", library,
                layer_set=rel.RelatingMaterial, material=concrete)
            layer.Name = "Structure"
            layer.LayerThickness = 200

            # Mark our wall type as a reusable asset in our library.
            ifcopenshell.api.run("project.assign_declaration", library,
                definition=wall_type, relating_context=context)

            # Let's imagine we're starting a new project
            model = ifcopenshell.api.run("project.create_file")
            project = ifcopenshell.api.run("root.create_entity", model, ifc_class="IfcProject", name="Test")

            # Now we can easily append our wall type from our libary
            wall_type = ifcopenshell.api.run("project.append_asset", model, library=library, element=wall_type)
        """
        self.file = file
        self.settings = {"library": library, "element": element}

    def execute(self):
        self.added_elements = {}
        self.whitelisted_inverse_attributes = {}
        if self.settings["element"].is_a("IfcTypeProduct"):
            self.target_class = "IfcTypeProduct"
            return self.append_type_product()
        elif self.settings["element"].is_a("IfcProduct"):
            self.target_class = "IfcProduct"
            return self.append_product()
        elif self.settings["element"].is_a("IfcMaterial"):
            self.target_class = "IfcMaterial"
            return self.append_material()
        elif self.settings["element"].is_a("IfcCostSchedule"):
            self.target_class = "IfcCostSchedule"
            return self.append_cost_schedule()
        elif self.settings["element"].is_a("IfcProfileDef"):
            self.target_class = "IfcProfileDef"
            return self.append_profile_def()

    def get_existing_element(self, element):
        if element.id() in self.added_elements:
            return self.added_elements[element.id()]
        try:
            if element.is_a("IfcRoot"):
                return self.file.by_guid(element.GlobalId)
            elif element.is_a("IfcMaterial"):
                return [e for e in self.file.by_type("IfcMaterial") if e.Name == element.Name][0]
            elif element.is_a("IfcProfileDef"):
                return [e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == element.ProfileName][0]
        except:
            return False

    def append_material(self):
        self.whitelisted_inverse_attributes = {
            "IfcMaterial": ["HasExternalReferences", "HasProperties", "HasRepresentation"]
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        if element.HasRepresentation:
            self.reuse_existing_contexts()
        return element

    def append_cost_schedule(self):
        self.whitelisted_inverse_attributes = {"IfcCostSchedule": ["Controls"], "IfcCostItem": ["IsNestedBy"]}
        return self.add_element(self.settings["element"])

    def append_profile_def(self):
        self.whitelisted_inverse_attributes = {"IfcProfileDef": ["HasProperties"]}
        return self.add_element(self.settings["element"])

    def append_type_product(self):
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcMaterialDefinition": ["HasExternalReferences", "HasProperties", "HasRepresentation"],
            "IfcRepresentationItem": ["StyledByItem"],
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        self.reuse_existing_contexts()
        return element

    def append_product(self):
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcObject": ["IsDefinedBy.IfcRelDefinesByProperties"],
            "IfcElement": ["HasOpenings"],
            "IfcMaterialDefinition": ["HasExternalReferences", "HasProperties", "HasRepresentation"],
            "IfcRepresentationItem": ["StyledByItem"],
        }
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        element = self.add_element(self.settings["element"])
        self.reuse_existing_contexts()

        element_type = ifcopenshell.util.element.get_type(self.settings["element"])
        if element_type:
            ifcopenshell.api.owner.settings.factory_reset()
            new_type = ifcopenshell.api.run(
                "project.append_asset", self.file, library=self.settings["library"], element=element_type
            )
            ifcopenshell.api.run(
                "type.assign_type",
                self.file,
                should_run_listeners=False,
                related_object=element,
                relating_type=new_type,
                should_map_representations=False,
            )
            ifcopenshell.api.owner.settings.restore()

        return element

    def add_element(self, element):
        if element.id() == 0:
            return
        existing_element = self.get_existing_element(element)
        if existing_element:
            return existing_element
        new = self.file.add(element)
        self.added_elements[element.id()] = new
        self.check_inverses(element)
        subelement_queue = self.settings["library"].traverse(element, max_levels=1)[1:]
        while subelement_queue:
            subelement = subelement_queue.pop(0)
            existing_element = self.get_existing_element(subelement)
            if existing_element:
                self.added_elements[subelement.id()] = existing_element
                if not self.has_whitelisted_inverses(existing_element):
                    self.check_inverses(subelement)
            else:
                self.added_elements[subelement.id()] = self.file.add(subelement)
                self.check_inverses(subelement)
                subelement_queue.extend(self.settings["library"].traverse(subelement, max_levels=1)[1:])
        return new

    def has_whitelisted_inverses(self, element):
        for source_class, attributes in self.whitelisted_inverse_attributes.items():
            if not element.is_a(source_class):
                continue
            for attribute in attributes:
                attribute_class = None
                if "." in attribute:
                    attribute, attribute_class = attribute.split(".")
                value = getattr(element, attribute, [])
                if attribute_class:
                    for subvalue in value:
                        if subvalue.is_a(attribute_class):
                            return True
                elif value:
                    return True

    def check_inverses(self, element):
        for source_class, attributes in self.whitelisted_inverse_attributes.items():
            if not element.is_a(source_class):
                continue
            for attribute in attributes:
                attribute_class = None
                if "." in attribute:
                    attribute, attribute_class = attribute.split(".")
                for inverse in getattr(element, attribute, []):
                    if attribute_class and inverse.is_a(attribute_class):
                        self.add_inverse_element(inverse)
                    elif not attribute_class:
                        self.add_inverse_element(inverse)

    def add_inverse_element(self, element):
        # Inverse attributes are added manually because they are basically
        # relationships that can reference many other assets that we are not
        # interested in.
        new = self.file.create_entity(element.is_a())
        for i, attribute in enumerate(element):
            new_attribute = None
            if isinstance(attribute, ifcopenshell.entity_instance):
                if not self.is_another_asset(attribute):
                    new_attribute = self.add_element(attribute)
            elif isinstance(attribute, tuple) and attribute and isinstance(attribute[0], ifcopenshell.entity_instance):
                new_attribute = []
                for item in attribute:
                    if not self.is_another_asset(item):
                        new_attribute.append(self.add_element(item))
            else:
                new_attribute = attribute
            if new_attribute is not None:
                new[i] = new_attribute

    def is_another_asset(self, element):
        if element == self.settings["element"]:
            return False
        elif element.is_a("IfcFeatureElement"):
            # Feature elements match the target class but aren't considered "assets"
            return False
        elif element.is_a(self.target_class):
            return True
        elif self.target_class == "IfcProduct" and element.is_a("IfcTypeProduct"):
            return True
        return False

    def reuse_existing_contexts(self):
        added_contexts = set([e for e in self.added_elements.values() if e.is_a("IfcGeometricRepresentationContext")])
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
        for added_context in added_contexts:
            ifcopenshell.util.element.remove_deep2(self.file, added_context)

    def get_equivalent_existing_context(self, added_context):
        for context in self.existing_contexts:
            if context.is_a() != added_context.is_a():
                continue
            if context.is_a("IfcGeometricRepresentationSubContext"):
                if (
                    context.ContextType == added_context.ContextType
                    and context.ContextIdentifier == added_context.ContextIdentifier
                    and context.TargetView == added_context.TargetView
                ):
                    return context
            elif (
                context.ContextType == added_context.ContextType
                and context.ContextIdentifier == added_context.ContextIdentifier
            ):
                return context

    def create_equivalent_context(self, added_context):
        if added_context.is_a("IfcGeometricRepresentationSubContext"):
            parent = self.get_equivalent_existing_context(added_context.ParentContext)
            if not parent:
                parent = self.create_equivalent_context(added_context.ParentContext)
            return ifcopenshell.api.run(
                "context.add_context",
                self.file,
                parent=parent,
                context_type=added_context.ContextType,
                context_identifier=added_context.ContextIdentifier,
                target_view=added_context.TargetView,
            )
        return ifcopenshell.api.run(
            "context.add_context",
            self.file,
            context_type=added_context.ContextType,
            context_identifier=added_context.ContextIdentifier,
        )
