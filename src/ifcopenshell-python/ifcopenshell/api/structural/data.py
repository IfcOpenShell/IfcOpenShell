class Data:
    is_loaded = False
    products = {}
    structural_analysis_models = {}
    boundary_conditions = {}
    connected_structural_members = {}
    connection_conditions = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.structural_analysis_models = {}
        cls.boundary_conditions = {}
        cls.connected_structural_members = {}
        cls.connection_conditions = {}

    @classmethod
    def load(cls, file, product_id=None):
        cls._file = file
        if not cls._file:
            return
        if product_id:
            return cls.load_structural_connection(product_id)
        cls.load_structural_analysis_models()
        cls.is_loaded = True

    @classmethod
    def load_structural_analysis_models(cls):
        cls.products = {}
        cls.structural_analysis_models = {}

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

            data["SharedPlacement"] = model.SharedPlacement.id()

            cls.structural_analysis_models[model.id()] = data

    @classmethod
    def load_structural_connection(cls, product_id):
        cls.boundary_conditions = {}
        cls.connected_structural_members = {}
        # cls.connection_conditions = {}

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

        cls.connected_structural_members[connection.id()] = {}
        for rel in connection.ConnectsStructuralMembers or []:
            data = rel.get_info()
            del data["OwnerHistory"]
            data["RelatingStructuralMember"] = rel.RelatingStructuralMember.id()
            data["RelatedStructuralConnection"] = rel.RelatedStructuralConnection.id()
            del data["ConditionCoordinateSystem"] # TODO: consider orientation
            del data["AppliedCondition"] # delete and parse below
            if rel.is_a("IfcRelConnectsWithEccentricity"):
                data["ConnectionConstraint"] = rel.ConnectionConstraint # TODO

            cls.connected_structural_members[connection.id()][rel.id()] = data

            if rel.AppliedCondition:
                data = rel.AppliedCondition.get_info()
                for key, value in data.items():
                    if not value or key in ["Name", "type", "id"]:
                        continue
                    data[key] = value.wrappedValue
            else:
                data = {}
            cls.connection_conditions[rel.id()] = data
        
        print(cls.connected_structural_members)
        print(cls.connection_conditions)

        # cls.connected_structural_members[connection.id()] = [
        #     rel.id()
        #     for rel in connection.ConnectsStructuralMembers or []
        # ]