import blenderbim.tool as tool


class ContextData:
    data = {}
    is_loaded = False

    @classmethod
    def load(cls):
        cls.data = {"contexts": cls.get_contexts()}
        cls.is_loaded = True

    @classmethod
    def get_contexts(cls):
        results = []
        for context in tool.Ifc.get().by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            results.append(
                {"id": context.id(), "context_type": context.ContextType, "subcontexts": cls.get_subcontexts(context)}
            )
        return results

    @classmethod
    def get_subcontexts(cls, context):
        results = []
        for subcontext in context.HasSubContexts:
            results.append(
                {
                    "id": subcontext.id(),
                    "context_type": subcontext.ContextType,
                    "context_identifier": subcontext.ContextIdentifier,
                    "target_view": subcontext.TargetView,
                }
            )
        return results
