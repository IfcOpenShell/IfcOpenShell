# This file was generated with the assistance of an AI coding tool.
import ifcopenshell
import ifcopenshell.api.context
import ifcopenshell.api.geometry
import ifcopenshell.api.root
import ifcopenshell.api.unit
import ifcopenshell.geom


class TestSelectRay:
    def test_hit_instance_is_an_entity_instance(self):
        f = ifcopenshell.file(schema="IFC4")
        ifcopenshell.api.root.create_entity(f, ifc_class="IfcProject")
        ifcopenshell.api.unit.assign_unit(f)
        model = ifcopenshell.api.context.add_context(f, context_type="Model")
        body = ifcopenshell.api.context.add_context(
            f, context_type="Model", context_identifier="Body", target_view="MODEL_VIEW", parent=model
        )
        wall = ifcopenshell.api.root.create_entity(f, ifc_class="IfcWall")
        representation = ifcopenshell.api.geometry.add_wall_representation(
            f, context=body, length=5.0, height=3.0, thickness=0.2
        )
        ifcopenshell.api.geometry.assign_representation(f, product=wall, representation=representation)

        tree = ifcopenshell.geom.tree()
        settings = ifcopenshell.geom.settings()
        settings.set("iterator-output", ifcopenshell.ifcopenshell_wrapper.NATIVE)
        iterator = ifcopenshell.geom.iterator(settings, f)
        assert iterator.initialize()
        while True:
            tree.add_element(iterator.get())
            if not iterator.next():
                break

        hits = tree.select_ray((2.5, -5.0, 1.5), (0.0, 1.0, 0.0), 10.0)
        assert len(hits) > 0
        assert hits[0].instance.is_a("IfcWall")
        assert f.by_id(hits[0].instance.id()) == wall
