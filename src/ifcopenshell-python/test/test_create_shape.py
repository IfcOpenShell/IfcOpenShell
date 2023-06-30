import ifcopenshell
import ifcopenshell.api
import ifcopenshell.geom
import ifcopenshell.api.owner.settings

class TestAssignObject:
    def test_no_welding_on_distinct_items(self):
        self.file = ifcopenshell.api.run("project.create_file")
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]
    
        ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcProject", name="Test"
        )
        unit = ifcopenshell.api.run(
            "unit.add_si_unit", self.file, unit_type="LENGTHUNIT"
        )
        ifcopenshell.api.run("unit.assign_unit", self.file, units=[unit])
        context = ifcopenshell.api.run(
            "context.add_context", self.file, context_type="Model"
        )
        element = ifcopenshell.api.run(
            "root.create_entity", self.file, ifc_class="IfcWall"
        )

        def create_extrusion(x, y):
            points = (
                (x + 0.0, y + 0.0),
                (x + 0.0, y + 1.0),
                (x + 1.0, y + 1.0),
                (x + 1.0, y + 0.0),
                (x + 0.0, y + 0.0),
            )
            curve = self.file.createIfcPolyline(
                [self.file.createIfcCartesianPoint(p) for p in points]
            )
            extrusion_direction = self.file.createIfcDirection((0.0, 0.0, 1.0))
            return self.file.createIfcExtrudedAreaSolid(
                self.file.createIfcArbitraryClosedProfileDef("AREA", None, curve),
                self.file.createIfcAxis2Placement3D(
                    self.file.createIfcCartesianPoint((0.0, 0.0, 0.0)),
                ),
                extrusion_direction,
                1.0,
            )

        extrusions = [create_extrusion(x, 0.0) for x in [0.0, 1.0]]
        element.Representation = self.file.createIfcProductDefinitionShape(
            Representations=[
                self.file.createIfcShapeRepresentation(
                    context,
                    context.ContextIdentifier,
                    "SweptSolid",
                    extrusions,
                )
            ]
        )

        obj = ifcopenshell.geom.create_shape(
            ifcopenshell.geom.settings(WELD_VERTICES=True), element
        )

        # item_ids is a per-triangle array, so we have 12 triangles per cube
        # even though not documented, the order in representation items should match
        assert (
            obj.geometry.item_ids
            == (extrusions[0].id(),) * 12 + (extrusions[1].id(),) * 12
        )

        # group the vertices
        vs = [
            obj.geometry.verts[i : i + 3] for i in range(0, len(obj.geometry.verts), 3)
        ]

        # welding should not happen between distinct items so the total number of verts should be 2 times 8
        assert len(vs) == 16

        # even though there are only 12 unique vertices as the cubes are touching
        assert len(set(vs)) == 12


if __name__ == "__main__":
    import pytest

    pytest.main(["-vvsx", __file__])
