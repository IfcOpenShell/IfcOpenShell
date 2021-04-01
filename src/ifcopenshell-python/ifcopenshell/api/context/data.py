class Data:
    is_loaded = False
    contexts = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.contexts = {}

    @classmethod
    def load(cls, file):
        if not file:
            return
        cls.contexts = {}
        for context in file.by_type("IfcGeometricRepresentationContext", include_subtypes=False):
            subcontexts = {}
            for subcontext in context.HasSubContexts:
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
