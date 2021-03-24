class Data:
    is_loaded = False
    products = {}
    boundary_conditions = {}
    structural_analysis_models = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.boundary_conditions = {}
        cls.connected_structural_members = {}
        cls.structural_analysis_models = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if product_id:
            cls.boundary_conditions = {}
            return cls.load_structural_connection(product_id)
        cls.products = {}
        cls.structural_analysis_models = {}
        cls.load_structural_analysis_models()
        cls.is_loaded = True

    @classmethod
    def load_structural_analysis_models(cls):
        for model in cls._file.by_type("IfcStructuralAnalysisModel"):
            if model.IsGroupedBy:
                for rel in model.IsGroupedBy:
                    for product in rel.RelatedObjects:
                        cls.products.setdefault(product.id(), []).append(model.id())
            data = model.get_info()
            del data["OwnerHistory"]
            del data["OrientationOf2DPlane"]

            loaded_by = []
            for load_group in model.LoadedBy or []:
                loaded_by.append(load_group.id())
            data["LoadedBy"] = loaded_by

            has_results = []
            for result_group in model.HasResults or []:
                has_results.append(result_group.id())
            data["HasResults"] = has_results

            cls.structural_analysis_models[model.id()] = data

    @classmethod
    def load_structural_connection(cls, product_id):
        connection = cls._file.by_id(product_id)
        if connection.AppliedCondition:
            data = connection.AppliedCondition.get_info()
            for key, value in data.items():
                if not value or key in ["Name", "type", "id"]:
                    continue
                data[key] = value.wrappedValue
        else:
            data = {}
        cls.boundary_conditions[connection.id()] = data

        cls.connected_structural_members[connection.id()] = [
            rel.RelatingStructuralMember.id()
            for rel in connection.ConnectsStructuralMembers or []
        ]

