import ifcopenshell.util.unit


class Usecase:
    def __init__(self, file, settings=None):
        # TODO: This usecase currently depends on Blender's data model
        self.file = file
        self.settings = {
            "context": None,  # IfcGeometricRepresentationContext
            "geometry": None,  # This is (currently) a Blender data object, hence this depends on Blender now
            "total_items": 1,  # How many representation items to create
            "unit_scale": None,  # A scale factor to apply for all vectors in case the unit is different
            "should_force_faceted_brep": False,  # If we should force faceted breps for meshes
            "is_wireframe": False,  # If the geometry is a wireframe
            "is_curve": False,  # If the geometry is a Blender curve
            "is_point_cloud": False,  # If the geometry is a point cloud
        }
        self.ifc_vertices = []
        for key, value in settings.items():
            self.settings[key] = value
        self.context_of_items = None

    def execute(self):
        if self.settings["unit_scale"] is None:
            self.settings["unit_scale"] = self.calculate_unit_scale()
        if self.settings["context"].ContextType == "Model":
            return self.create_model_representation()
        elif self.settings["context"].ContextType == "Plan":
            return self.create_plan_representation()
        return self.create_variable_representation()

    def calculate_unit_scale(self):
        units = self.file.by_type("IfcUnitAssignment")[0]
        unit_scale = 1
        for unit in units.Units:
            if not hasattr(unit, "UnitType") or unit.UnitType != "LENGTHUNIT":
                continue
            while unit.is_a("IfcConversionBasedUnit"):
                unit_scale *= unit.ConversionFactor.ValueComponent.wrappedValue
                unit = unit.ConversionFactor.UnitComponent
            if unit.is_a("IfcSIUnit"):
                unit_scale *= ifcopenshell.util.unit.get_prefix_multiplier(unit.Prefix)
        return unit_scale

    def create_model_representation(self):
        if self.settings["context"].is_a() == "IfcGeometricRepresentationContext":
            return self.create_variable_representation()
        if self.settings["context"].ContextIdentifier == "Annotation":
            return self.create_geometric_set_representation()
        elif self.settings["context"].ContextIdentifier == "Axis":
            return self.create_curve3d_representation()
        elif self.settings["context"].ContextIdentifier == "Body":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "Box":
            return self.create_box_representation()
        elif self.settings["context"].ContextIdentifier == "Clearance":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "CoG":
            return self.create_cog_representation()
        elif self.settings["context"].ContextIdentifier == "FootPrint":
            return self.create_variable_representation()
        elif self.settings["context"].ContextIdentifier == "Reference":
            if self.settings["context"].TargetView == "GRAPH_VIEW":
                return self.create_structural_reference_representation()
        elif self.settings["context"].ContextIdentifier == "Profile":
            return self.create_curve3d_representation()
        elif self.settings["context"].ContextIdentifier == "SurveyPoints":
            return self.create_geometric_curve_set_representation()

    def create_plan_representation(self):
        if self.settings["context"].ContextIdentifier == "Annotation":
            if self.settings["is_text"]:
                return self.create_text_representation()
            shape_representation = self.create_geometric_curve_set_representation(is_2d=True)
            shape_representation.RepresentationType = "Annotation2D"
            return shape_representation
        elif self.settings["context"].ContextIdentifier == "Axis":
            return self.create_curve2d_representation()
        elif self.settings["context"].ContextIdentifier == "Body":
            pass
        elif self.settings["context"].ContextIdentifier == "Box":
            pass
        elif self.settings["context"].ContextIdentifier == "Clearance":
            pass
        elif self.settings["context"].ContextIdentifier == "CoG":
            pass
        elif self.settings["context"].ContextIdentifier == "FootPrint":
            if self.settings["context"].TargetView in ["PLAN_VIEW", "REFLECTED_PLAN_VIEW"]:
                return self.create_geometric_curve_set_representation(is_2d=True)
        elif self.settings["context"].ContextIdentifier == "Reference":
            pass
        elif self.settings["context"].ContextIdentifier == "Profile":
            pass
        elif self.settings["context"].ContextIdentifier == "SurveyPoints":
            pass

    def create_variable_representation(self):
        if self.settings["is_wireframe"]:
            return self.create_wireframe_representation()
        elif self.settings["is_curve"]:
            return self.create_curve_representation()
        elif self.settings["is_point_cloud"]:
            return self.create_point_cloud_representation()
        return self.create_mesh_representation()

    def create_mesh_representation(self):
        if self.file.schema == "IFC2X3" or self.settings["should_force_faceted_brep"]:
            return self.create_faceted_brep()
        return self.create_polygonal_face_set()

    def create_faceted_brep(self):
        self.create_vertices()
        ifc_raw_items = [None] * self.settings["total_items"]
        for i, value in enumerate(ifc_raw_items):
            ifc_raw_items[i] = []
        for polygon in self.settings["geometry"].polygons:
            ifc_raw_items[polygon.material_index % self.settings["total_items"]].append(
                self.file.createIfcFace(
                    [
                        self.file.createIfcFaceOuterBound(
                            self.file.createIfcPolyLoop([self.ifc_vertices[vertice] for vertice in polygon.vertices]),
                            True,
                        )
                    ]
                )
            )
        # TODO: May not actually be a closed shell, but who checks anyway?
        items = [self.file.createIfcFacetedBrep(self.file.createIfcClosedShell(i)) for i in ifc_raw_items if i]
        return self.file.createIfcShapeRepresentation(
            self.settings["context"],
            self.settings["context"].ContextIdentifier,
            "Brep",
            items,
        )

    def create_vertices(self, is_2d=False):
        if is_2d:
            for v in self.settings["geometry"].vertices:
                co = self.convert_si_to_unit(v.co)
                self.ifc_vertices.append(self.file.createIfcCartesianPoint((co[0], co[1])))
            return
        self.ifc_vertices.extend(
            [
                self.file.createIfcCartesianPoint(self.convert_si_to_unit(v.co))
                for v in self.settings["geometry"].vertices
            ]
        )

    def convert_si_to_unit(self, co):
        return co / self.settings["unit_scale"]
