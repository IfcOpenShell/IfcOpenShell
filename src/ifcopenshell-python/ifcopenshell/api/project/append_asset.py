import ifcopenshell
import ifcopenshell.api


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
        elif self.settings["element"].is_a("IfcMaterial"):
            return self.append_material()
        elif self.settings["element"].is_a("IfcCostSchedule"):
            return self.append_cost_schedule()
        elif self.settings["element"].is_a("IfcProfileDef"):
            return self.append_profile_def()

    def is_already_appended(self):
        try:
            self.file.by_guid(self.settings["element"].GlobalId)
            return True
        except:
            return False

    def append_material(self):
        if [e for e in self.file.by_type("IfcMaterial") if e.Name == self.settings["element"].Name]:
            return
        return self.file.add(self.settings["element"])

    def append_cost_schedule(self):
        if self.is_already_appended():
            return
        self.whitelisted_inverse_attributes = {"IfcCostSchedule": ["Controls"], "IfcCostItem": ["IsNestedBy"]}
        return self.add_element(self.settings["element"])

    def append_profile_def(self):
        if [e for e in self.file.by_type("IfcProfileDef") if e.ProfileName == self.settings["element"].ProfileName]:
            return
        self.whitelisted_inverse_attributes = {"IfcProfileDef": ["HasProperties"]}
        return self.add_element(self.settings["element"])

    def append_type_product(self):
        if self.is_already_appended():
            return
        self.whitelisted_inverse_attributes = {
            "IfcObjectDefinition": ["HasAssociations"],
            "IfcMaterialDefinition": ["HasExternalReferences", "HasProperties"],
            "IfcRepresentationItem": ["StyledByItem"],
        }
        element = self.add_element(self.settings["element"])
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        added_contexts = [e for e in self.file.traverse(element) if e.is_a("IfcGeometricRepresentationContext")]
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
        for added_context in added_contexts:
            ifcopenshell.util.element.remove_deep(self.file, added_context)
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
        inverse_attributes = []
        [inverse_attributes.extend(v) for k, v in self.whitelisted_inverse_attributes.items() if element.is_a(k)]
        inverse_attributes = set(inverse_attributes)
        for attribute in inverse_attributes:
            for inverse in getattr(element, attribute, []):
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
