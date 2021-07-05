def get_context(ifc_file, context, subcontext=None, target_view=None):
    if subcontext or target_view:
        elements = ifc_file.by_type("IfcGeometricRepresentationSubContext")
    else:
        elements = ifc_file.by_type("IfcGeometricRepresentationContext", include_subtypes=False)
    for element in elements:
        if context and element.ContextType != context:
            continue
        if subcontext and getattr(element, "ContextIdentifier") != subcontext:
            continue
        if target_view and getattr(element, "TargetView") != target_view:
            continue
        return element


def is_representation_of_context(representation, context, subcontext=None, target_view=None):
    if target_view is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.TargetView == target_view
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif subcontext is not None:
        return (
            representation.ContextOfItems.is_a("IfcGeometricRepresentationSubContext")
            and representation.ContextOfItems.ContextIdentifier == subcontext
            and representation.ContextOfItems.ContextType == context
        )
    elif representation.ContextOfItems.ContextType == context:
        return True


def get_representation(element, context, subcontext=None, target_view=None):
    if element.is_a("IfcProduct") and element.Representation:
        for r in element.Representation.Representations:
            if is_representation_of_context(r, context, subcontext, target_view):
                return r
    elif element.is_a("IfcTypeProduct") and element.RepresentationMaps:
        for r in element.RepresentationMaps:
            if is_representation_of_context(r.MappedRepresentation, context, subcontext, target_view):
                return r.MappedRepresentation
