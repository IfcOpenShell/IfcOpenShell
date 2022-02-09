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
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"library": None, "element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        self.added_elements = set()
        self.whitelisted_inverse_attributes = {}
        if self.settings["element"].is_a("IfcTypeProduct"):
            return self.append_type_product()
        elif self.settings["element"].is_a("IfcProduct"):
            return self.append_product()
        elif self.settings["element"].is_a("IfcMaterial"):
            return self.append_material()
        elif self.settings["element"].is_a("IfcCostSchedule"):
            return self.append_cost_schedule()
        elif self.settings["element"].is_a("IfcProfileDef"):
            return self.append_profile_def()

    def get_existing_element(self):
        try:
            return self.file.by_guid(self.settings["element"].GlobalId)
        except:
            return False

    def append_material(self):
        if [e for e in self.file.by_type("IfcMaterial") if e.Name == self.settings["element"].Name]:
            return
        return self.file.add(self.settings["element"])

    def append_cost_schedule(self):
        element = self.get_existing_element()
        if element:
            return element
        self.whitelisted_inverse_attributes = {"IfcCostSchedule": ["Controls"], "IfcCostItem": ["IsNestedBy"]}
        return self.add_element(self.settings["element"])

    def append_profile_def(self):
        if [e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == self.settings["element"].ProfileName]:
            return
        self.whitelisted_inverse_attributes = {"IfcProfileDef": ["HasProperties"]}
        return self.add_element(self.settings["element"])

    def append_type_product(self):
        element = self.get_existing_element()
        if element:
            return element
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcMaterialDefinition": ["HasExternalReferences", "HasProperties"],
            "IfcRepresentationItem": ["StyledByItem"],
        }
        element = self.add_element(self.settings["element"])
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        added_contexts = [e for e in self.file.traverse(element) if e.is_a() == "IfcGeometricRepresentationContext"]
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
        for added_context in added_contexts:
            ifcopenshell.util.element.remove_deep(self.file, added_context)
        return element

    def append_product(self):
        element = self.get_existing_element()
        if element:
            return element
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcObject": ["IsDefinedBy.IfcRelDefinesByProperties"],
            "IfcElement": ["HasOpenings"],
            "IfcMaterialDefinition": ["HasExternalReferences", "HasProperties"],
            "IfcRepresentationItem": ["StyledByItem"],
        }
        element = self.add_element(self.settings["element"])
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        added_contexts = [e for e in self.file.traverse(element) if e.is_a() == "IfcGeometricRepresentationContext"]
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
        for added_context in added_contexts:
            ifcopenshell.util.element.remove_deep(self.file, added_context)

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
            )
            ifcopenshell.api.owner.settings.restore()

        return element

    def add_element(self, element):
        if element.id() == 0 or element.id() in self.added_elements:
            return
        new = self.file.add(element)
        self.added_elements.add(element.id())
        self.add_inverse(element)
        for subelement in self.settings["library"].traverse(element):
            self.add_inverse(subelement)
        return new

    def add_inverse(self, element):
        for source_class, attributes in self.whitelisted_inverse_attributes.items():
            if not element.is_a(source_class):
                continue
            for attribute in attributes:
                attribute_class = None
                if "." in attribute:
                    attribute, attribute_class = attribute.split(".")
                for inverse in getattr(element, attribute, []):
                    if attribute_class and inverse.is_a(attribute_class):
                        self.add_element(inverse)
                    elif not attribute_class:
                        self.add_element(inverse)

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
            return ifcopenshell.api.run(
                "context.add_context",
                context=added_context.ContextType,
                subcontext=added_context.ContextIdentifier,
                target_view=added_context.TargetView,
            )
        return ifcopenshell.api.run(
            "context.add_context", context=added_context.ContextType, subcontext=added_context.ContextIdentifier
        )
