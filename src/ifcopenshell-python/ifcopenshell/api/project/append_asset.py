import ifcopenshell
import ifcopenshell.api


class Usecase:
    def __init__(self, file, **settings):
        self.file = file
        self.settings = {"element": None}
        for key, value in settings.items():
            self.settings[key] = value

    def execute(self):
        element = self.file.add(self.settings["element"])
        self.existing_contexts = self.file.by_type("IfcGeometricRepresentationContext")
        added_contexts = [e for e in self.file.traverse(element) if e.is_a("IfcGeometricRepresentationContext")]
        for added_context in added_contexts:
            equivalent_existing_context = self.get_equivalent_existing_context(added_context)
            if not equivalent_existing_context:
                equivalent_existing_context = self.create_equivalent_context(added_context)
            for inverse in self.file.get_inverse(added_context):
                ifcopenshell.util.element.replace_attribute(inverse, added_context, equivalent_existing_context)
        for added_context in added_contexts:
            if added_context.is_a() == "IfcGeometricRepresentationContext":
                ifcopenshell.util.element.remove_deep(self.file, added_context)
        return element

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
