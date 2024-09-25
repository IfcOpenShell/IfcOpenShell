import pytest
import test.bootstrap
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.owner.settings
import ifcopenshell.api.project
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom
import ifcopenshell.ifcopenshell_wrapper as W
import ifcopenshell.util.shape
from ifcopenshell.util.shape_builder import ShapeBuilder, V
from typing import get_args


class TestGeomSettings:
    def test_settings(self):
        settings = ifcopenshell.geom.settings()
        assert set(get_args(ifcopenshell.geom.SETTING)) == set(settings.setting_names())

        assert "use-python-opencascade" in settings.setting_names()
        assert settings.get(settings.USE_PYTHON_OPENCASCADE) is False
        assert settings.get("use-python-opencascade") is False
        assert "USE_PYTHON_OPENCASCADE = False" in repr(settings)

        # Testing both new and old ways of setting geometry settings.
        if ifcopenshell.geom.has_occ:
            settings.set("use-python-opencascade", True)
            settings.set(settings.USE_PYTHON_OPENCASCADE, True)
            assert settings.get(settings.USE_PYTHON_OPENCASCADE) is True
            assert "USE_PYTHON_OPENCASCADE = True" in repr(settings)
        else:
            with pytest.raises(AttributeError):
                settings.set("use-python-opencascade", True)
            with pytest.raises(AttributeError):
                settings.set(settings.USE_PYTHON_OPENCASCADE, True)
            assert "USE_PYTHON_OPENCASCADE = False" in repr(settings)

    def test_serializer_settings(self):
        settings = ifcopenshell.geom.serializer_settings()
        assert set(get_args(ifcopenshell.geom.SERIALIZER_SETTING)) == set(settings.setting_names())

        # Only for settings.
        assert "use-python-opencascade" not in settings.setting_names()
        with pytest.raises(AttributeError):
            settings.get(settings.USE_PYTHON_OPENCASCADE)
        with pytest.raises(RuntimeError):
            settings.get("use-python-opencascade")
        with pytest.raises(RuntimeError):
            settings.set("use-python-opencascade", True)
        assert "USE_PYTHON_OPENCASCADE" not in repr(settings)


class TestTriangulationAttributes(test.bootstrap.IFC4):
    def test_faces_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        extrusion = builder.extrude(builder.rectangle(), magnitude=1.0)
        representation = builder.get_representation(context, extrusion)
        settings = ifcopenshell.geom.settings()
        shape = ifcopenshell.geom.create_shape(settings, representation)
        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        faces = ifcopenshell.util.shape.get_faces(shape)
        assert set(faces_item_ids) == {extrusion.id()}
        assert len(faces) == 12  # Cube has 12 tris.
        assert len(faces_item_ids) == len(faces)

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {extrusion.id()}
        assert len(edges) == 12  # Cube has 12 edges.
        assert len(edges_item_ids) == len(edges)

    def test_curve_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        curve = builder.rectangle()
        representation = builder.get_representation(context, curve)
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, representation)

        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        assert len(faces_item_ids) == 0

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {curve.id()}
        assert len(edges) == 4
        assert len(edges_item_ids) == len(edges)

    def test_mixed_representation_item_ids(self):
        ifc_file = ifcopenshell.file()
        ifcopenshell.api.root.create_entity(ifc_file, ifc_class="IfcProject", name="Test")
        context = ifcopenshell.api.context.add_context(ifc_file, context_type="Model")

        builder = ShapeBuilder(ifc_file)
        curve = builder.rectangle()

        fill = ifc_file.create_entity("IfcAnnotationFillArea", builder.rectangle())
        representation = builder.get_representation(context, (curve, fill))
        settings = ifcopenshell.geom.settings()
        settings.set("dimensionality", W.CURVES_SURFACES_AND_SOLIDS)
        shape = ifcopenshell.geom.create_shape(settings, representation)

        faces_item_ids = ifcopenshell.util.shape.get_faces_representation_item_ids(shape)
        faces = ifcopenshell.util.shape.get_faces(shape)
        assert len(faces) == 2  # Fill area will produce a triangulated face.
        assert set(faces_item_ids) == {fill.id()}
        assert len(faces_item_ids) == len(faces)

        edges_item_ids = ifcopenshell.util.shape.get_edges_representation_item_ids(shape)
        edges = ifcopenshell.util.shape.get_edges(shape)
        assert set(edges_item_ids) == {fill.id(), curve.id()}
        assert len(edges) == 8  # 4 edges rectangle curve + 4 edges fill area
        assert len(edges_item_ids) == len(edges)


class TestAssignObject:
    def test_no_welding_on_distinct_items(self):
        self.file = ifcopenshell.api.project.create_file()
        ifcopenshell.api.owner.settings.get_user = lambda ifc: (ifc.by_type("IfcPersonAndOrganization") or [None])[0]
        ifcopenshell.api.owner.settings.get_application = lambda ifc: (ifc.by_type("IfcApplication") or [None])[0]

        ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcProject", name="Test")
        unit = ifcopenshell.api.unit.add_si_unit(self.file, unit_type="LENGTHUNIT")
        ifcopenshell.api.unit.assign_unit(self.file, units=[unit])
        context = ifcopenshell.api.context.add_context(self.file, context_type="Model")
        element = ifcopenshell.api.root.create_entity(self.file, ifc_class="IfcWall")

        def create_extrusion(x, y):
            points = (
                (x + 0.0, y + 0.0),
                (x + 0.0, y + 1.0),
                (x + 1.0, y + 1.0),
                (x + 1.0, y + 0.0),
                (x + 0.0, y + 0.0),
            )
            curve = self.file.createIfcPolyline([self.file.createIfcCartesianPoint(p) for p in points])
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

        obj = ifcopenshell.geom.create_shape(ifcopenshell.geom.settings(WELD_VERTICES=True), element)

        # item_ids is a per-triangle array, so we have 12 triangles per cube
        # even though not documented, the order in representation items should match
        assert obj.geometry.item_ids == (extrusions[0].id(),) * 12 + (extrusions[1].id(),) * 12

        # group the vertices
        vs = [obj.geometry.verts[i : i + 3] for i in range(0, len(obj.geometry.verts), 3)]

        # welding should not happen between distinct items so the total number of verts should be 2 times 8
        assert len(vs) == 16

        # even though there are only 12 unique vertices as the cubes are touching
        assert len(set(vs)) == 12


if __name__ == "__main__":
    import pytest

    pytest.main(["-vvsx", __file__])
