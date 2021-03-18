from blenderbim.bim.ifc import IfcStore


class Data:
    is_loaded = False
    products = {}
    structural_analysis_models = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.connections = {}
        cls.structural_analysis_models = {}

    @classmethod
    def load(cls, product_id=None):
        if product_id:
            cls.connections = {}
            return cls.load_structural_connection(product_id)
        cls.products = {}
        cls.structural_analysis_models = {}
        cls.load_structural_analysis_models()
        cls.is_loaded = True

    @classmethod
    def load_structural_analysis_models(cls):
        for model in IfcStore.get_file().by_type("IfcStructuralAnalysisModel"):
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
        connection = IfcStore.get_file().by_id(product_id)
        if connection.AppliedCondition:
            data = connection.AppliedCondition.get_info()
            for key, value in data.items():
                if not value or key in ["Name", "type", "id"]:
                    continue
                data[key] = value.wrappedValue
        else:
            data = {}
        cls.connections[connection.id()] = data
