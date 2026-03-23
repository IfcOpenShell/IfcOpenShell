# Bonsai - OpenBIM Blender Add-on
# Copyright (C) 2021 Dion Moult <dion@thinkmoult.com>
#
# This file is part of Bonsai.
#
# Bonsai is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Bonsai is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Bonsai.  If not, see <http://www.gnu.org/licenses/>.

import bonsai.core.spatial as subject
from test.core.bootstrap import collector, ifc, spatial


class TestReferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run("spatial.reference_structure", products=["element"], relating_structure="structure").should_be_called()
        subject.reference_structure(ifc, spatial, structure="structure", element="element")


class TestDereferenceStructure:
    def test_run(self, ifc, spatial):
        spatial.can_reference("structure", "element").should_be_called().will_return(True)
        ifc.run(
            "spatial.dereference_structure", products=["element"], relating_structure="structure"
        ).should_be_called()
        subject.dereference_structure(ifc, spatial, structure="structure", element="element")


class TestAssignContainer:
    def test_run(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_root_element("element").should_be_called().will_return("aggregate")
        spatial.get_decomposition("aggregate").should_be_called().will_return(["element", "element2"])
        spatial.can_contain("container", "aggregate").should_be_called().will_return(True)
        ifc.run("spatial.assign_container", products=["aggregate"], relating_structure="container").should_be_called()
        spatial.disable_editing("obj").should_be_called()
        ifc.get_object("aggregate").should_be_called().will_return("aggregate_obj")
        ifc.get_object("element").should_be_called().will_return("obj")
        ifc.get_object("element2").should_be_called().will_return("obj2")
        collector.assign("aggregate_obj").should_be_called()
        collector.assign("obj").should_be_called()
        collector.assign("obj2").should_be_called()
        subject.assign_container(ifc, collector, spatial, container="container", objs=["obj"])


class TestEnableEditingContainer:
    def test_run(self, spatial):
        spatial.set_target_container_as_default().should_be_called()
        spatial.enable_editing("obj").should_be_called()
        subject.enable_editing_container(spatial, obj="obj")


class TestDisableEditingContainer:
    def test_run(self, spatial):
        spatial.disable_editing("obj").should_be_called()
        subject.disable_editing_container(spatial, obj="obj")


class TestRemoveContainer:
    def test_run(self, ifc, collector):
        ifc.get_entity("obj").should_be_called().will_return("element")
        ifc.run("spatial.unassign_container", products=["element"]).should_be_called()
        collector.assign("obj").should_be_called()
        subject.remove_container(ifc, collector, obj="obj")


class TestCopyToContainer:
    def test_run(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.get_relative_object_matrix("obj", "container_obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])

    def test_using_an_absolute_matrix_if_there_is_no_from_container(self, ifc, collector, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return(None)
        spatial.get_object_matrix("obj").should_be_called().will_return("matrix")

        ifc.get_object("to_container").should_be_called().will_return("to_container_obj")
        spatial.duplicate_object_and_data("obj").should_be_called().will_return("new_obj")
        spatial.set_relative_object_matrix("new_obj", "to_container_obj", "matrix").should_be_called()
        spatial.run_root_copy_class(obj="new_obj").should_be_called()
        spatial.run_spatial_assign_container(container="to_container", objs=["new_obj"]).should_be_called()

        spatial.disable_editing("obj").should_be_called()

        subject.copy_to_container(ifc, collector, spatial, obj="obj", containers=["to_container"])


class TestSelectContainer:
    def test_run(self, ifc, spatial):
        ifc.get_object("container").should_be_called().will_return("container_obj")
        spatial.set_active_object("container_obj", selection_mode="ADD").should_be_called()
        subject.select_container(ifc, spatial, container="container", selection_mode="ADD")


class TestSelectSimilarContainer:
    def test_run(self, ifc, spatial):
        ifc.get_entity("obj").should_be_called().will_return("element")
        spatial.get_container("element").should_be_called().will_return("container")
        spatial.get_decomposed_elements("container", True).should_be_called().will_return(["contained_element"])
        spatial.select_products(["contained_element"]).should_be_called()
        subject.select_similar_container(ifc, spatial, obj="obj")


class TestDeleteContainer:
    SPATIAL_TYPES = {"IfcProject", "IfcSite", "IfcBuilding", "IfcBuildingStorey", "IfcSpace"}

    class _Element:
        def __init__(self, element_id, ifc_class, object_type=None):
            self._id = element_id
            self._ifc_class = ifc_class
            self.ObjectType = object_type
            self.IsDecomposedBy = []

        def id(self):
            return self._id

        def is_a(self, ifc_class):
            if self._ifc_class == ifc_class:
                return True
            if ifc_class in {"IfcSpatialElement", "IfcSpatialStructureElement", "IfcExternalSpatialStructureElement"}:
                return self._ifc_class in TestDeleteContainer.SPATIAL_TYPES
            return False

    class _RelAssignsToProduct:
        def __init__(self, relating_product, related_objects):
            self.RelatingProduct = relating_product
            self.RelatedObjects = tuple(related_objects)

        def is_a(self, ifc_class):
            return ifc_class == "IfcRelAssignsToProduct"

    class _RelAggregates:
        def __init__(self, related_objects):
            self.RelatedObjects = tuple(related_objects)

    class _IfcFile:
        def __init__(self, elements, inverse_map=None):
            self.elements = elements
            self.inverse_map = inverse_map or {}

        def by_id(self, element_id):
            return self.elements[element_id]

        def get_inverse(self, element):
            return self.inverse_map.get(element.id(), [])

    @staticmethod
    def _run_delete(
        monkeypatch,
        *,
        container,
        ifc_file,
        decomposition,
        container_lookup=None,
        missing_obj_ids=None,
        default_container=None,
        guessed_default=None,
        include_root=False,
        props_default_container=0,
    ):
        container_lookup = container_lookup or {}
        missing_obj_ids = missing_obj_ids or set()
        events = {"deleted_objects": [], "run_calls": [], "imported": [], "set_default_calls": []}

        monkeypatch.setattr(
            subject.ifcopenshell.util.element, "get_decomposition", lambda element, is_recursive=True: decomposition
        )
        monkeypatch.setattr(
            subject.ifcopenshell.util.element, "get_container", lambda element: container_lookup.get(element)
        )

        class FakeIfc:
            @staticmethod
            def get():
                return ifc_file

            @staticmethod
            def get_object(element):
                return None if element.id() in missing_obj_ids else f"obj-{element.id()}"

            @staticmethod
            def run(usecase, **kwargs):
                events["run_calls"].append((usecase, kwargs))

        class FakeGeometry:
            @staticmethod
            def delete_ifc_object(obj, allow_auto_annotation_deletion=False, suppress_spatial_import=False):
                events["deleted_objects"].append((obj, allow_auto_annotation_deletion, suppress_spatial_import))

        class FakeSpatialProps:
            default_container = props_default_container

        class FakeSpatial:
            @staticmethod
            def import_spatial_decomposition():
                events["imported"].append(True)

            @staticmethod
            def guess_default_container():
                return guessed_default

            @staticmethod
            def set_default_container(new_container):
                events["set_default_calls"].append(new_container)

            @staticmethod
            def get_spatial_props():
                return FakeSpatialProps

        if include_root:
            class FakeRoot:
                @staticmethod
                def get_default_container():
                    return default_container

            subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container, root=FakeRoot)
        else:
            subject.delete_container(FakeIfc, FakeSpatial, FakeGeometry, container=container)

        return events, FakeSpatialProps

    def test_run_cascades_container_and_dependent_annotations(self, monkeypatch):
        container = self._Element(1, "IfcBuilding")
        storey = self._Element(2, "IfcBuildingStorey")
        wall = self._Element(3, "IfcWall")
        section_level = self._Element(4, "IfcAnnotation", object_type="SECTION_LEVEL")
        container.IsDecomposedBy = [self._RelAggregates([storey])]

        ifc_file = self._IfcFile(
            {1: container, 2: storey, 3: wall, 4: section_level},
            {2: [self._RelAssignsToProduct(storey, [section_level])]},
        )
        events, _ = self._run_delete(
            monkeypatch,
            container=container,
            ifc_file=ifc_file,
            decomposition={storey, wall},
            container_lookup={wall: storey},
            missing_obj_ids={3},
        )

        assert events["deleted_objects"] == [
            ("obj-4", True, True),
            ("obj-1", False, True),
            ("obj-2", False, True),
        ]
        assert events["run_calls"] == [("root.remove_product", {"product": wall})]
        assert events["imported"] == [True]

    def test_does_not_delete_elements_outside_spatial_subtree(self, monkeypatch):
        container = self._Element(1, "IfcBuilding")
        own_storey = self._Element(2, "IfcBuildingStorey")
        other_storey = self._Element(3, "IfcBuildingStorey")
        own_wall = self._Element(4, "IfcWall")
        outside_wall = self._Element(5, "IfcWall")
        container.IsDecomposedBy = [self._RelAggregates([own_storey])]

        ifc_file = self._IfcFile({1: container, 2: own_storey, 3: other_storey, 4: own_wall, 5: outside_wall})
        events, _ = self._run_delete(
            monkeypatch,
            container=container,
            ifc_file=ifc_file,
            decomposition={own_storey, own_wall, outside_wall},
            container_lookup={own_wall: own_storey, outside_wall: other_storey},
        )

        assert events["deleted_objects"] == [
            ("obj-1", False, True),
            ("obj-2", False, True),
            ("obj-4", False, True),
        ]
        assert events["run_calls"] == []
        assert events["imported"] == [True]

    def test_reassigns_default_container_after_cascade_if_deleted(self, monkeypatch):
        container = self._Element(1, "IfcBuilding")
        storey = self._Element(2, "IfcBuildingStorey")
        replacement_storey = self._Element(3, "IfcBuildingStorey")
        container.IsDecomposedBy = [self._RelAggregates([storey])]
        ifc_file = self._IfcFile({1: container, 2: storey, 3: replacement_storey})

        events, _ = self._run_delete(
            monkeypatch,
            container=container,
            ifc_file=ifc_file,
            decomposition={storey},
            include_root=True,
            default_container=storey,
            guessed_default=replacement_storey,
            props_default_container=2,
        )
        assert events["set_default_calls"] == [replacement_storey]
        assert events["imported"] == [True]

    def test_keeps_default_container_if_not_deleted(self, monkeypatch):
        container = self._Element(1, "IfcBuilding")
        deleted_storey = self._Element(2, "IfcBuildingStorey")
        surviving_storey = self._Element(3, "IfcBuildingStorey")
        container.IsDecomposedBy = [self._RelAggregates([deleted_storey])]
        ifc_file = self._IfcFile({1: container, 2: deleted_storey, 3: surviving_storey})

        events, _ = self._run_delete(
            monkeypatch,
            container=container,
            ifc_file=ifc_file,
            decomposition={deleted_storey},
            include_root=True,
            default_container=surviving_storey,
            guessed_default=deleted_storey,
            props_default_container=3,
        )
        assert events["set_default_calls"] == []

    def test_clears_default_container_if_deleted_and_no_replacement(self, monkeypatch):
        container = self._Element(1, "IfcBuilding")
        storey = self._Element(2, "IfcBuildingStorey")
        container.IsDecomposedBy = [self._RelAggregates([storey])]
        ifc_file = self._IfcFile({1: container, 2: storey})

        events, props = self._run_delete(
            monkeypatch,
            container=container,
            ifc_file=ifc_file,
            decomposition={storey},
            include_root=True,
            default_container=storey,
            guessed_default=None,
            props_default_container=2,
        )
        assert events["set_default_calls"] == []
        assert props.default_container == 0
