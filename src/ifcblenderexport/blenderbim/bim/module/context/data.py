from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    contexts = {}

    @classmethod
    def load(cls):
        file = IfcStore.get_file()
        if not file:
            return
        cls.contexts = {}
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            subcontexts = {}
            # See bug #1224 for why we don't use HasSubContexts
            for subcontext in file.by_type("IfcGeometricRepresentationSubContext"):
                if subcontext.ParentContext != context:
                    continue
                subcontexts[int(subcontext.id())] = {
                    "ContextType": subcontext.ContextType,
                    "ContextIdentifier": subcontext.ContextIdentifier,
                    "TargetView": subcontext.TargetView,
                }
            cls.contexts[int(context.id())] = {
                "ContextType": context.ContextType,
                "HasSubContexts": subcontexts
            }
        cls.is_loaded = True
