import ifcopenshell
import ifcopenshell.api.feature
import ifcopenshell.geom
import ifcopenshell.api
import ifcopenshell.util.unit

import numpy as np

import propertygroups

O = 0.0, 0.0, 0.0
X = 1.0, 0.0, 0.0
Y = 0.0, 1.0, 0.0
Z = 0.0, 0.0, 1.0


class Context:
    model = None
    body = None
    storey = None

    def __init__(self):
        self._create_empty_model()

    def clear(self):
        self._create_empty_model()

    def open(self, file_content):
        self.model = ifcopenshell.file.from_string(file_content)
        body = [ctx for ctx in self.model.by_type('IfcGeometricRepresentationContext') if ctx.ContextIdentifier == 'Body']
        if body:
            self.body = body[0]
        else:
            context = ifcopenshell.api.run("context.add_context", self.model, context_type="Model")
            self.body = ifcopenshell.api.run(
                "context.add_context",
                self.model,
                context_type="Model",
                context_identifier="Body",
                target_view="MODEL_VIEW",
                parent=context,
            )
        axis = [ctx for ctx in self.model.by_type('IfcGeometricRepresentationContext') if ctx.ContextIdentifier == 'Axis']
        if body:
            self.axis = axis[0]
        else:
            context = ifcopenshell.api.run("context.add_context", self.model, context_type="Model")
            self.axis = ifcopenshell.api.run(
                "context.add_context",
                self.model,
                context_type="Model",
                context_identifier="Axis",
                target_view="GRAPH_VIEW",
                parent=context,
            )
        self.storey = self.model.by_type('IfcBuildingStorey')[0]

    def _create_empty_model(self):
        # Create a blank model
        self.model = ifcopenshell.file()
        # All projects must have one IFC Project element
        project = ifcopenshell.api.run(
            "root.create_entity", self.model, ifc_class="IfcProject", name="My Project"
        )
        # Geometry is optional in IFC, but because we want to use geometry in this example, let's define units
        # Assigning without arguments defaults to metric units
        ifcopenshell.api.run("unit.assign_unit", self.model)
        # Let's create a modeling geometry context, so we can store 3D geometry (note: IFC supports 2D too!)
        context = ifcopenshell.api.run("context.add_context", self.model, context_type="Model")
        # In particular, in this example we want to store the 3D "body" geometry of objects, i.e. the body shape
        self.body = ifcopenshell.api.run(
            "context.add_context",
            self.model,
            context_type="Model",
            context_identifier="Body",
            target_view="MODEL_VIEW",
            parent=context,
        )
        self.axis = ifcopenshell.api.run(
            "context.add_context",
            self.model,
            context_type="Model",
            context_identifier="Axis",
            target_view="GRAPH_VIEW",
            parent=context,
        )
        # Create a site, building, and storey. Many hierarchies are possible.
        site = ifcopenshell.api.run(
            "root.create_entity", self.model, ifc_class="IfcSite", name="My Site"
        )
        building = ifcopenshell.api.run(
            "root.create_entity", self.model, ifc_class="IfcBuilding", name="Building A"
        )
        self.storey = ifcopenshell.api.run(
            "root.create_entity",
            self.model,
            ifc_class="IfcBuildingStorey",
            name="Ground Floor",
        )
        # Since the site is our top level location, assign it to the project
        # Then place our building on the site, and our storey in the building
        ifcopenshell.api.run(
            "aggregate.assign_object",
            self.model,
            relating_object=project,
            products=[site],
        )
        ifcopenshell.api.run(
            "aggregate.assign_object",
            self.model,
            relating_object=site,
            products=[building],
        )
        ifcopenshell.api.run(
            "aggregate.assign_object",
            self.model,
            relating_object=building,
            products=[self.storey],
        )

    def create_2pt_wall(
        self, p1, p2, elevation, height, thickness, container, wall_type=None
    ):
        p1 = np.array([p1[0], p1[1]])
        p2 = np.array([p2[0], p2[1]])

        wall = ifcopenshell.api.run("root.create_entity", self.model, ifc_class="IfcWall")
        length = float(np.linalg.norm(p2 - p1))
        representation = ifcopenshell.api.run(
            "geometry.add_wall_representation",
            self.model,
            context=self.body,
            length=length,
            height=height,
            thickness=thickness,
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            self.model,
            product=wall,
            representation=representation,
        )
        representation = ifcopenshell.api.run(
            "geometry.add_axis_representation",
            self.model,
            context=self.axis,
            axis=[(0.0, 0.0), (length, 0.0)],
        )
        ifcopenshell.api.run(
            "geometry.assign_representation",
            self.model,
            product=wall,
            representation=representation,
        )
        v = p2 - p1
        v = np.divide(v, float(np.linalg.norm(v)), casting="unsafe")
        matrix = np.array(
            [
                [v[0], -v[1], 0, p1[0]],
                [v[1], v[0], 0, p1[1]],
                [0, 0, 1, elevation],
                [0, 0, 0, 1],
            ]
        )
        ifcopenshell.api.run("geometry.edit_object_placement", self.model, product=wall, matrix=matrix)
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.model,
            relating_structure=container,
            products=[wall],
        )
        if wall_type:
            ifcopenshell.api.run(
                "type.assign_type",
                self.model,
                related_object=wall,
                relating_type=wall_type,
            )

        return wall

    def get_element(self, guid):
        return self.model[guid]

    def get_model(self):
        return self.model

    def create_fill(self, ty, pt, wall):
        if isinstance(wall, str):
            wall = self.model[wall]
        if not wall.is_a('IfcWall'):
            raise ValueError("Only 'wall' hosts are supported")
        if ty == 'door':
            props = propertygroups.BIMDoorProperties()
        elif ty == 'window':
            props = propertygroups.BIMWindowProperties()
        else:
            raise ValueError("Only 'door' or 'window' fills are supported")
        si_conversion = ifcopenshell.util.unit.calculate_unit_scale(self.model)
        body = ifcopenshell.util.representation.get_context(
            self.model, "Model", "Body", "MODEL_VIEW"
        )
        representation_data = props.to_dict(si_conversion=si_conversion)
        representation_data["context"] = body
        door_representation = ifcopenshell.api.run(
            f"geometry.add_{ty}_representation", self.model, **representation_data
        )
        door = ifcopenshell.api.run(
            "root.create_entity", self.model, ifc_class=f"ifc{ty}"
        )
        door.OverallWidth = props.overall_width / si_conversion
        door.OverallHeight = props.overall_height / si_conversion
        ifcopenshell.api.run(
            "geometry.assign_representation",
            self.model,
            product=door,
            representation=door_representation,
        )
        ifcopenshell.api.run(
            "spatial.assign_container",
            self.model,
            relating_structure=self.storey,
            products=[door],
        )

        r = [
            r
            for r in wall.Representation.Representations
            if r.RepresentationIdentifier == "Axis"
        ]
        if not r:
            raise ValueError("Axis representation is needed")
        r = r[0]
        axis_geometry = ifcopenshell.geom.create_shape(
            ifcopenshell.geom.settings(
                DIMENSIONALITY=ifcopenshell.ifcopenshell_wrapper.CURVES_SURFACES_AND_SOLIDS,
                USE_WORLD_COORDS=True,
            ),
            wall,
            r,
        )
        vs = np.array(axis_geometry.geometry.verts).reshape((-1, 3))
        es = np.array(axis_geometry.geometry.edges).reshape((-1, 2))
        A, B = vs[es[0]]
        v = B - A
        P = np.zeros(3)
        P[0 : len(pt)] = pt
        AP = P - A
        AP_dot_v = np.dot(AP, v)
        v_dot_v = np.dot(v, v)
        t = AP_dot_v / v_dot_v * np.linalg.norm(v) / si_conversion

        opening = ifcopenshell.api.run(
            "root.create_entity",
            self.model,
            ifc_class="IfcOpeningElement",
            predefined_type="OPENING",
            name="Opening",
        )

        position_3d = None
        if self.model.schema == "IFC2X3":
            position_3d = self.model.createIfcAxis2Placement2D(
                self.model.createIfcCartesianPoint([0.0, 0.0, 0.0])
            )
        position_2d = self.model.createIfcAxis2Placement2D(
            self.model.createIfcCartesianPoint([door.OverallWidth / 2.0, 0.0])
        )

        opening.Representation = self.model.createIfcProductDefinitionShape(
            Representations=[
                self.model.createIfcShapeRepresentation(
                    body,
                    "Body",
                    "SweptSolid",
                    Items=[
                        self.model.createIfcExtrudedAreaSolid(
                            self.model.createIfcRectangleProfileDef(
                                "AREA",
                                None,
                                position_2d,
                                door.OverallWidth,
                                1.2 / si_conversion,
                            ),
                            position_3d,
                            self.model.createIfcDirection((0.0, 0.0, 1.0)),
                            door.OverallHeight,
                        )
                    ],
                )
            ]
        )

        ifcopenshell.api.feature.add_feature(self.model, feature=opening, element=wall)
        ifcopenshell.api.feature.add_filling(self.model, opening=opening, element=door)

        z_offsets = {
            'door': 0,
            'window': 1
        }
        opening.ObjectPlacement = self.model.createIfcLocalPlacement(
            wall.ObjectPlacement,
            self.model.createIfcAxis2Placement3D(
                self.model.createIfcCartesianPoint((float(t), 0.0, z_offsets[ty] / si_conversion))
            ),
        )

        door.ObjectPlacement = self.model.createIfcLocalPlacement(
            opening.ObjectPlacement,
            self.model.createIfcAxis2Placement3D(
                self.model.createIfcCartesianPoint((0.0, 0.0, 0.0))
            ),
        )

        return door

    def to_obj_file(self, fn):
        st = ifcopenshell.geom.settings(USE_WORLD_COORDS=True, WELD_VERTICES=False)
        it = ifcopenshell.geom.iterator(st, self.model, exclude=("IfcOpeningElement",))
        sr = ifcopenshell.geom.serializers.obj(
            fn, fn + ".mtl", st, ifcopenshell.geom.serializer_settings()
        )
        if it.initialize():
            for el in ifcopenshell.geom.consume_iterator(it):
                sr.write(el)
            sr.finalize()


if __name__ == "__main__":
    m = Context()
    w1 = m.create_2pt_wall((0.0, 0.0), (4.0, 0.0), 0.0, 3.0, 0.1, m.storey)
    w2 = m.create_2pt_wall((1.0, 3.0), (1.0, 0.0), 0.0, 3.0, 0.1, m.storey)
    m.create_fill('door', [2, 0.0], w1)
    m.create_fill('window', [1, 1.5], w2)
    m.model.write("out.ifc")
    m.to_obj_file("out.obj")
