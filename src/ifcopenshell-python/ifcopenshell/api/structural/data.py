class Data:
    is_loaded = False
    products = {}
    structural_analysis_models = {}
    connections = {}
    boundary_conditions = {}
    connects_structural_members = {}

    @classmethod
    def purge(cls):
        cls.is_loaded = False
        cls.products = {}
        cls.structural_analysis_models = {}
        cls.connections = {}
        cls.boundary_conditions = {}
        cls.connects_structural_members = {}

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

            data["SharedPlacement"] = model.SharedPlacement.id() if model.SharedPlacement else None

            cls.structural_analysis_models[model.id()] = data

    @classmethod
    def load_structural_connection(cls, product_id):
        cls.connections = {}
        cls.boundary_conditions = {}
        cls.connects_structural_members = {}

        connection = cls._file.by_id(product_id)
        connection_data = {"AppliedCondition": None, "ConnectsStructuralMembers": []}

        if connection.AppliedCondition:
            cls.load_boundary_condition(connection.AppliedCondition)
            connection_data["AppliedCondition"] = connection.AppliedCondition.id()

        for rel in connection.ConnectsStructuralMembers or []:
            cls.load_connects_structural_member(rel)
            connection_data["ConnectsStructuralMembers"].append(rel.id())

        cls.connections[connection.id()] = connection_data

    @classmethod
    def load_boundary_condition(cls, boundary_condition):
        data = boundary_condition.get_info()
        for key, value in data.items():
            if not value or key in ["Name", "type", "id"]:
                continue
            data[key] = value.wrappedValue
        cls.boundary_conditions[boundary_condition.id()] = data

    @classmethod
    def load_connects_structural_member(cls, rel):
        rel_data = rel.get_info()
        del rel_data["OwnerHistory"]
        rel_data["RelatingStructuralMember"] = rel.RelatingStructuralMember.id()
        rel_data["RelatedStructuralConnection"] = rel.RelatedStructuralConnection.id()
        del rel_data["ConditionCoordinateSystem"]  # TODO: consider orientation

        if rel.is_a("IfcRelConnectsWithEccentricity"):
            rel_data["ConnectionConstraint"] = rel.ConnectionConstraint  # TODO

        if rel.AppliedCondition:
            cls.load_boundary_condition(rel.AppliedCondition)
            rel_data["AppliedCondition"] = rel.AppliedCondition.id()

        cls.connects_structural_members[rel.id()] = rel_data
